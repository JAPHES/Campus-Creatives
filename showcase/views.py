from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.db.models import Avg, Count
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from projects.models import Project, ProjectMembership

from .forms import RatingForm, ShowcaseForm
from .models import Rating, ShowcaseCredit, ShowcaseEntry


def showcase_list(request):
    entries = (
        ShowcaseEntry.objects.filter(is_published=True)
        .select_related("project__idea__campus")
        .prefetch_related("credits__user__profile")
    )
    return render(request, "showcase/list.html", {"entries": entries})


def showcase_detail(request, pk):
    entry = get_object_or_404(
        ShowcaseEntry.objects.select_related("project__idea__campus").prefetch_related("credits__user__profile"),
        pk=pk,
        is_published=True,
    )
    is_team_member = request.user.is_authenticated and entry.project.is_member(request.user)
    rated_ids = set()
    if is_team_member:
        rated_ids = set(Rating.objects.filter(project=entry.project, rater=request.user).values_list("rated_user_id", flat=True))
    ratings = entry.project.ratings.select_related("rater__profile", "rated_user__profile")
    return render(
        request,
        "showcase/detail.html",
        {
            "entry": entry,
            "is_team_member": is_team_member,
            "rated_ids": rated_ids,
            "ratings": ratings,
            "rating_summary": ratings.aggregate(average=Avg("score"), count=Count("id")),
        },
    )


@login_required
def publish_showcase(request, project_pk):
    project = get_object_or_404(Project.objects.select_related("idea"), pk=project_pk, owner=request.user)
    if project.status != Project.Status.COMPLETED:
        messages.error(request, "Finish the project before publishing it.")
        return redirect("projects:workspace", pk=project.pk)
    try:
        entry = project.showcase_entry
    except ShowcaseEntry.DoesNotExist:
        entry = None
    form = ShowcaseForm(request.POST or None, request.FILES or None, instance=entry, initial={"title": project.idea.title, "description": project.idea.description})
    if request.method == "POST" and form.is_valid():
        entry = form.save(commit=False)
        entry.project = project
        entry.is_published = True
        entry.published_at = timezone.now()
        entry.full_clean()
        entry.save()
        for membership in project.memberships.select_related("user"):
            ShowcaseCredit.objects.update_or_create(
                entry=entry,
                user=membership.user,
                defaults={"role": membership.role},
            )
        messages.success(request, "Your finished project is now in the showcase.")
        return redirect("showcase:detail", pk=entry.pk)
    return render(request, "showcase/publish.html", {"form": form, "project": project, "entry": entry})


@login_required
def rate_member(request, pk, user_pk):
    entry = get_object_or_404(ShowcaseEntry.objects.select_related("project"), pk=pk, is_published=True)
    rated_user = get_object_or_404(get_user_model(), pk=user_pk)
    if not entry.project.is_member(request.user):
        return HttpResponseForbidden("Only project team members can leave ratings.")
    if not ProjectMembership.objects.filter(project=entry.project, user=rated_user).exists() or rated_user == request.user:
        return HttpResponseForbidden("You can only rate another member of this project.")
    if Rating.objects.filter(project=entry.project, rater=request.user, rated_user=rated_user).exists():
        messages.info(request, "You have already rated this teammate for this project.")
        return redirect("showcase:detail", pk=entry.pk)
    form = RatingForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        rating = form.save(commit=False)
        rating.project = entry.project
        rating.rater = request.user
        rating.rated_user = rated_user
        rating.full_clean()
        rating.save()
        messages.success(request, "Thanks—your teammate rating was saved.")
        return redirect("showcase:detail", pk=entry.pk)
    return render(request, "showcase/rate.html", {"form": form, "entry": entry, "rated_user": rated_user})
