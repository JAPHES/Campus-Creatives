from datetime import timedelta

from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from accounts.models import User
from creatives.models import Campus, Skill
from ideas.models import Idea

from .models import Invitation, Project, ProjectMembership, Task


@override_settings(PASSWORD_HASHERS=["django.contrib.auth.hashers.MD5PasswordHasher"])
class CollaborationFlowTests(TestCase):
    def setUp(self):
        self.campus = Campus.objects.create(name="Flow University")
        self.skill = Skill.objects.create(name="Film")
        self.owner = User.objects.create_user(email="owner@example.com", password="password")
        self.collaborator = User.objects.create_user(email="collab@example.com", password="password")
        for user, name in ((self.owner, "Owner"), (self.collaborator, "Collaborator")):
            user.profile.name = name
            user.profile.campus = self.campus
            user.profile.save()
            user.profile.skills.add(self.skill)
        self.idea = Idea.objects.create(
            owner=self.owner,
            title="One collaborator project",
            description="Test the complete flow.",
            campus=self.campus,
            budget_type=Idea.BudgetType.PAID,
            deadline=timezone.localdate() + timedelta(days=7),
        )
        self.idea.skills_needed.add(self.skill)

    def test_one_accepted_collaborator_can_activate_workspace(self):
        invitation = Invitation.objects.create(
            idea=self.idea,
            invitee=self.collaborator,
            invited_by=self.owner,
            role="Editor",
        )
        self.client.force_login(self.collaborator)
        self.client.post(reverse("projects:respond", args=[invitation.pk, "accept"]))
        invitation.refresh_from_db()
        self.assertEqual(invitation.status, Invitation.Status.ACCEPTED)
        self.client.force_login(self.owner)
        response = self.client.post(reverse("projects:activate", args=[self.idea.pk]))
        project = Project.objects.get(idea=self.idea)
        self.assertRedirects(response, reverse("projects:workspace", args=[project.pk]))
        self.assertEqual(project.memberships.count(), 2)
        self.assertTrue(project.memberships.filter(user=self.collaborator, role="Editor").exists())

    def test_duplicate_invitation_is_prevented(self):
        self.client.force_login(self.owner)
        url = reverse("ideas:invite", args=[self.idea.pk, self.collaborator.profile.pk])
        self.client.post(url, {"role": "Editor", "message": "Join us"})
        self.client.post(url, {"role": "Editor", "message": "Join us again"})
        self.assertEqual(Invitation.objects.filter(idea=self.idea, invitee=self.collaborator).count(), 1)

    def test_non_member_cannot_view_workspace(self):
        project = Project.objects.create(idea=self.idea, owner=self.owner)
        ProjectMembership.objects.create(project=project, user=self.owner, role="Owner", is_owner=True)
        outsider = User.objects.create_user(email="outsider@example.com", password="password")
        self.client.force_login(outsider)
        response = self.client.get(reverse("projects:workspace", args=[project.pk]))
        self.assertEqual(response.status_code, 403)

    def test_member_can_render_workspace(self):
        project = Project.objects.create(idea=self.idea, owner=self.owner)
        ProjectMembership.objects.create(project=project, user=self.owner, role="Owner", is_owner=True)
        Task.objects.create(project=project, title="Plan the shoot", created_by=self.owner, assignee=self.owner)
        self.client.force_login(self.owner)
        response = self.client.get(reverse("projects:workspace", args=[project.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Plan the shoot")

    def test_unrelated_member_cannot_edit_another_members_task(self):
        project = Project.objects.create(idea=self.idea, owner=self.owner)
        ProjectMembership.objects.create(project=project, user=self.owner, role="Owner", is_owner=True)
        ProjectMembership.objects.create(project=project, user=self.collaborator, role="Editor")
        third = User.objects.create_user(email="third@example.com", password="password")
        ProjectMembership.objects.create(project=project, user=third, role="Writer")
        task = Task.objects.create(project=project, title="Edit footage", created_by=self.owner, assignee=self.collaborator)
        self.client.force_login(third)
        response = self.client.get(reverse("projects:task_edit", args=[task.pk]))
        self.assertEqual(response.status_code, 403)
