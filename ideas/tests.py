from datetime import timedelta

from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from accounts.models import User
from creatives.models import Campus, Skill

from .models import Idea


@override_settings(PASSWORD_HASHERS=["django.contrib.auth.hashers.MD5PasswordHasher"])
class IdeaMatchingTests(TestCase):
    def setUp(self):
        self.campus = Campus.objects.create(name="Match University")
        self.other_campus = Campus.objects.create(name="Other University")
        self.design = Skill.objects.create(name="Design")
        self.video = Skill.objects.create(name="Video")
        self.owner = User.objects.create_user(email="owner@example.com", password="password")
        self.owner.profile.name = "Owner"
        self.owner.profile.campus = self.campus
        self.owner.profile.save()
        self.idea = Idea.objects.create(
            owner=self.owner,
            title="A campus film",
            description="Make a documentary.",
            campus=self.campus,
            budget_type=Idea.BudgetType.FREE,
            deadline=timezone.localdate() + timedelta(days=10),
        )
        self.idea.skills_needed.set([self.design, self.video])

    def test_matches_prioritize_available_creative_with_more_skills(self):
        best = User.objects.create_user(email="best@example.com", password="password")
        best.profile.name = "Best Match"
        best.profile.campus = self.campus
        best.profile.is_available = True
        best.profile.save()
        best.profile.skills.set([self.design, self.video])
        partial = User.objects.create_user(email="partial@example.com", password="password")
        partial.profile.name = "Partial Match"
        partial.profile.campus = self.other_campus
        partial.profile.is_available = False
        partial.profile.save()
        partial.profile.skills.set([self.design])
        self.client.force_login(self.owner)
        response = self.client.get(reverse("ideas:detail", args=[self.idea.pk]))
        matches = list(response.context["matches"])
        self.assertEqual(matches[0], best.profile)
        self.assertEqual(matches[0].skill_match_count, 2)
        self.assertTrue(matches[0].same_campus)

    def test_idea_requires_login_to_create(self):
        response = self.client.get(reverse("ideas:create"))
        self.assertRedirects(response, f"{reverse('accounts:login')}?next={reverse('ideas:create')}")
