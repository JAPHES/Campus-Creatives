from django.contrib.auth.decorators import login_required
from django.shortcuts import render


def landing(request):
    from ideas.models import Idea
    from showcase.models import ShowcaseEntry

    return render(
        request,
        "core/landing.html",
        {
            "featured_ideas": Idea.objects.filter(status=Idea.Status.OPEN).select_related("campus", "owner__profile").prefetch_related("skills_needed")[:3],
            "featured_work": ShowcaseEntry.objects.filter(is_published=True).select_related("project")[:3],
        },
    )


@login_required
def dashboard(request):
    from ideas.models import Idea
    from projects.models import Invitation, Project

    return render(
        request,
        "core/dashboard.html",
        {
            "my_ideas": Idea.objects.filter(owner=request.user).prefetch_related("skills_needed")[:4],
            "my_projects": Project.objects.filter(memberships__user=request.user).select_related("idea").distinct()[:4],
            "incoming_count": Invitation.objects.filter(invitee=request.user, status=Invitation.Status.PENDING).count(),
        },
    )
