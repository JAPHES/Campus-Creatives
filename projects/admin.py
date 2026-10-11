from django.contrib import admin

from .models import DiscussionMessage, Invitation, Project, ProjectMembership, Task


@admin.register(Invitation)
class InvitationAdmin(admin.ModelAdmin):
    list_display = ("idea", "invitee", "source", "status", "role", "created_at")
    list_filter = ("source", "status", "created_at")
    search_fields = ("idea__title", "invitee__email", "role")


class MembershipInline(admin.TabularInline):
    model = ProjectMembership
    extra = 0


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ("idea", "owner", "status", "created_at", "completed_at")
    list_filter = ("status", "created_at")
    search_fields = ("idea__title", "owner__email")
    inlines = (MembershipInline,)


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ("title", "project", "assignee", "status", "due_date")
    list_filter = ("status", "due_date")
    search_fields = ("title", "description", "project__idea__title")


@admin.register(DiscussionMessage)
class DiscussionMessageAdmin(admin.ModelAdmin):
    list_display = ("project", "author", "created_at")
    search_fields = ("body", "project__idea__title", "author__email")
