from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

from ideas.models import Idea


class Invitation(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        ACCEPTED = "accepted", "Accepted"
        DECLINED = "declined", "Declined"

    class Source(models.TextChoices):
        INVITATION = "invitation", "Owner invitation"
        APPLICATION = "application", "Creative application"

    idea = models.ForeignKey(Idea, on_delete=models.CASCADE, related_name="invitations")
    invitee = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="project_invitations")
    invited_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="invitations_sent")
    role = models.CharField(max_length=100, default="Collaborator")
    message = models.TextField(max_length=500, blank=True)
    source = models.CharField(max_length=20, choices=Source.choices, default=Source.INVITATION)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    created_at = models.DateTimeField(auto_now_add=True)
    responded_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ("-created_at",)
        constraints = [models.UniqueConstraint(fields=("idea", "invitee"), name="unique_idea_invitee")]
        indexes = [models.Index(fields=["invitee", "status"])]

    def __str__(self):
        return f"{self.invitee} — {self.idea}"


class Project(models.Model):
    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        COMPLETED = "completed", "Completed"

    idea = models.OneToOneField(Idea, on_delete=models.PROTECT, related_name="project")
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="owned_projects")
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ACTIVE)
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ("-created_at",)

    def __str__(self):
        return self.idea.title

    def is_member(self, user):
        return user.is_authenticated and self.memberships.filter(user=user).exists()


class ProjectMembership(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="memberships")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="project_memberships")
    role = models.CharField(max_length=100, default="Collaborator")
    is_owner = models.BooleanField(default=False)
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-is_owner", "joined_at")
        constraints = [models.UniqueConstraint(fields=("project", "user"), name="unique_project_member")]

    def __str__(self):
        return f"{self.user} on {self.project}"


class Task(models.Model):
    class Status(models.TextChoices):
        TODO = "todo", "To Do"
        IN_PROGRESS = "in_progress", "In Progress"
        REVIEW = "review", "Review"
        DONE = "done", "Done"

    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="tasks")
    title = models.CharField(max_length=160)
    description = models.TextField(max_length=1000, blank=True)
    assignee = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="assigned_tasks")
    due_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.TODO)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="created_tasks")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("due_date", "created_at")
        indexes = [models.Index(fields=["project", "status"])]

    def __str__(self):
        return self.title

    def clean(self):
        if self.assignee_id and not ProjectMembership.objects.filter(project=self.project, user=self.assignee).exists():
            raise ValidationError({"assignee": "The assignee must be a member of this project."})

    def can_manage(self, user):
        return user == self.project.owner or user == self.created_by or user == self.assignee


class DiscussionMessage(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="messages")
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="project_messages")
    body = models.TextField(max_length=1000)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("created_at",)

    def __str__(self):
        return f"{self.author} in {self.project}"
