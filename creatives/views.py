from django.db.models import Avg, Count, Q
from django.shortcuts import get_object_or_404, render

from .models import Campus, CreativeProfile, Skill


def creative_list(request):
    profiles = CreativeProfile.objects.select_related("campus", "user").prefetch_related("skills")
    query = request.GET.get("q", "").strip()
    campus_id = request.GET.get("campus", "")
    skill_id = request.GET.get("skill", "")
    availability = request.GET.get("availability", "")
    if query:
        profiles = profiles.filter(Q(name__icontains=query) | Q(bio__icontains=query) | Q(skills__name__icontains=query)).distinct()
    if campus_id:
        profiles = profiles.filter(campus_id=campus_id)
    if skill_id:
        profiles = profiles.filter(skills__id=skill_id)
    if availability == "available":
        profiles = profiles.filter(is_available=True)
    return render(
        request,
        "creatives/list.html",
        {
            "profiles": profiles,
            "campuses": Campus.objects.filter(is_active=True),
            "skills": Skill.objects.filter(is_active=True),
            "filters": {"q": query, "campus": campus_id, "skill": skill_id, "availability": availability},
        },
    )


def profile_detail(request, pk):
    profile = get_object_or_404(
        CreativeProfile.objects.select_related("campus", "user").prefetch_related("skills", "portfolio_links"), pk=pk
    )
    rating_summary = profile.user.ratings_received.filter(project__status="completed").aggregate(
        average=Avg("score"), count=Count("id")
    )
    can_view_contact = request.user.is_authenticated and (request.user == profile.user or profile.show_whatsapp)
    return render(
        request,
        "creatives/detail.html",
        {"profile": profile, "rating_summary": rating_summary, "can_view_contact": can_view_contact},
    )
