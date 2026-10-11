from datetime import timedelta

from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from accounts.models import User
from creatives.models import Campus, Skill
from ideas.models import Idea
from projects.models import Project, ProjectMembership

from .models import Rating, ShowcaseCredit, ShowcaseEntry


@override_settings(PASSWORD_HASHERS=["django.contrib.auth.hashers.MD5PasswordHasher"])
class ShowcaseFlowTests(TestCase):
    def setUp(self):
        campus = Campus.objects.create(name="Showcase University")
        skill = Skill.objects.create(name="Photography")
        self.owner = User.objects.create_user(email="owner@show.test", password="password")
        self.member = User.objects.create_user(email="member@show.test", password="password")
        self.owner.profile.name = "Owner"
        self.owner.profile.save()
        self.member.profile.name = "Member"
        self.member.profile.save()
        idea = Idea.objects.create(
            owner=self.owner,
            title="Photo story",
            description="A finished campus photo story.",
            campus=campus,
            budget_type=Idea.BudgetType.FREE,
            deadline=timezone.localdate() + timedelta(days=2),
            status=Idea.Status.COMPLETED,
        )
        idea.skills_needed.add(skill)
        self.project = Project.objects.create(idea=idea, owner=self.owner, status=Project.Status.COMPLETED, completed_at=timezone.now())
        ProjectMembership.objects.create(project=self.project, user=self.owner, role="Project owner", is_owner=True)
        ProjectMembership.objects.create(project=self.project, user=self.member, role="Photographer")

    def test_owner_publishes_completed_project_with_team_credits(self):
        self.client.force_login(self.owner)
        response = self.client.post(
            reverse("showcase:publish", args=[self.project.pk]),
            {"title": "Photo story", "description": "The finished photo story.", "media_link": "https://example.com/work"},
        )
        entry = ShowcaseEntry.objects.get(project=self.project)
        self.assertRedirects(response, reverse("showcase:detail", args=[entry.pk]))
        self.assertTrue(entry.is_published)
        self.assertEqual(ShowcaseCredit.objects.filter(entry=entry).count(), 2)

    def test_teammate_can_only_rate_same_person_once_per_project(self):
        entry = ShowcaseEntry.objects.create(
            project=self.project,
            title="Photo story",
            description="Finished work",
            is_published=True,
            published_at=timezone.now(),
        )
        self.client.force_login(self.owner)
        url = reverse("showcase:rate", args=[entry.pk, self.member.pk])
        self.client.post(url, {"score": 5, "comment": "Excellent collaborator"})
        response = self.client.post(url, {"score": 4, "comment": "Second try"})
        self.assertRedirects(response, reverse("showcase:detail", args=[entry.pk]))
        self.assertEqual(Rating.objects.filter(project=self.project, rater=self.owner, rated_user=self.member).count(), 1)
