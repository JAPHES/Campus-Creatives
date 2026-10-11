from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import BooleanField, Case, Count, Q, Value, When
from django.shortcuts import get_object_or_404, redirect, render

from creatives.models import Campus, CreativeProfile, Skill
from projects.models import Invitation, Project

from .forms import CollaborationRequestForm, IdeaForm
from .models import Idea


def idea_list(request):
    ideas = Idea.objects.select_related("owner__profile", "campus").prefetch_related("skills_needed")
    query = request.GET.get("q", "").strip()
    campus_id = request.GET.get("campus", "")
    skill_id = request.GET.get("skill", "")
    status = request.GET.get("status", Idea.Status.OPEN)
    if query:
        ideas = ideas.filter(Q(title__icontains=query) | Q(description__icontains=query))
    if campus_id:
        ideas = ideas.filter(campus_id=campus_id)
    if skill_id:
        ideas = ideas.filter(skills_needed__id=skill_id)
    if status in Idea.Status.values:
        ideas = ideas.filter(status=status)
    return render(
        request,
        "ideas/list.html",
        {
            "ideas": ideas.distinct(),
            "campuses": Campus.objects.filter(is_active=True),
            "skills": Skill.objects.filter(is_active=True),
            "statuses": Idea.Status.choices,
            "filters": {"q": query, "campus": campus_id, "skill": skill_id, "status": status},
        },
    )


def _matched_creatives(idea):
    requested = idea.skills_needed.all()
    return (
        CreativeProfile.objects.exclude(user=idea.owner)
        .select_related("user", "campus")
        .prefetch_related("skills")
        .annotate(
            skill_match_count=Count("skills", filter=Q(skills__in=requested), distinct=True),
            same_campus=Case(
                When(campus=idea.campus, then=Value(True)),
                default=Value(False),
                output_field=BooleanField(),
            ),
        )
        .filter(skill_match_count__gt=0)
        .order_by("-is_available", "-skill_match_count", "-same_campus", "name")[:10]
    )


def idea_detail(request, pk):
    idea = get_object_or_404(
        Idea.objects.select_related("owner__profile", "campus").prefetch_related("skills_needed"), pk=pk
    )
    is_owner = request.user.is_authenticated and request.user == idea.owner
    existing_request = None
    invited_user_ids = set()
    if request.user.is_authenticated:
        existing_request = Invitation.objects.filter(idea=idea, invitee=request.user).first()
    if is_owner:
        invited_user_ids = set(Invitation.objects.filter(idea=idea).values_list("invitee_id", flat=True))
    project = Project.objects.filter(idea=idea).first()
    context = {
        "idea": idea,
        "is_owner": is_owner,
        "matches": _matched_creatives(idea) if is_owner and idea.status == Idea.Status.OPEN else [],
        "requested_skill_count": idea.skills_needed.count(),
        "invited_user_ids": invited_user_ids,
        "existing_request": existing_request,
        "request_form": CollaborationRequestForm(),
        "collaboration_requests": idea.invitations.select_related("invitee__profile").all() if is_owner else [],
        "accepted_count": idea.invitations.filter(status=Invitation.Status.ACCEPTED).count() if is_owner else 0,
        "project": project,
    }
    return render(request, "ideas/detail.html", context)


@login_required
def idea_create(request):
    form = IdeaForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        idea = form.save(commit=False)
        idea.owner = request.user
        idea.save()
        form.save_m2m()
        messages.success(request, "Your idea is live. Here are the creatives who match it best.")
        return redirect(idea)
    return render(request, "ideas/form.html", {"form": form})


@login_required
def invite_creative(request, pk, profile_pk):
    if request.method != "POST":
        return redirect("ideas:detail", pk=pk)
    idea = get_object_or_404(Idea, pk=pk, owner=request.user, status=Idea.Status.OPEN)
    profile = get_object_or_404(CreativeProfile, pk=profile_pk)
    if profile.user == request.user:
        messages.error(request, "You cannot invite yourself to your own idea.")
        return redirect(idea)
    form = CollaborationRequestForm(request.POST)
    if form.is_valid():
        invitation, created = Invitation.objects.get_or_create(
            idea=idea,
            invitee=profile.user,
            defaults={
                "invited_by": request.user,
                "role": form.cleaned_data["role"],
                "message": form.cleaned_data["message"],
                "source": Invitation.Source.INVITATION,
            },
        )
        if created:
            messages.success(request, f"Invitation sent to {profile.name}.")
        else:
            messages.info(request, f"{profile.name} already has a request for this idea.")
    else:
        messages.error(request, "Please check the invitation details and try again.")
    return redirect(idea)


@login_required
def apply_to_idea(request, pk):
    if request.method != "POST":
        return redirect("ideas:detail", pk=pk)
    idea = get_object_or_404(Idea, pk=pk, status=Idea.Status.OPEN)
    if idea.owner == request.user:
        messages.error(request, "You already own this idea.")
        return redirect(idea)
    form = CollaborationRequestForm(request.POST)
    if form.is_valid():
        application, created = Invitation.objects.get_or_create(
            idea=idea,
            invitee=request.user,
            defaults={
                "invited_by": request.user,
                "role": form.cleaned_data["role"],
                "message": form.cleaned_data["message"],
                "source": Invitation.Source.APPLICATION,
            },
        )
        if created:
            messages.success(request, "Your collaboration request has been sent to the idea owner.")
        else:
            messages.info(request, "You already have a request for this idea.")
    else:
        messages.error(request, "Please check your request and try again.")
    return redirect(idea)
