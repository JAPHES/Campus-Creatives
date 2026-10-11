from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from ideas.models import Idea

from .forms import MessageForm, TaskForm
from .models import Invitation, Project, ProjectMembership, Task


def _ensure_membership(project, invitation):
    if invitation.status == Invitation.Status.ACCEPTED and Project.objects.filter(pk=project.pk).exists():
        ProjectMembership.objects.get_or_create(
            project=project,
            user=invitation.invitee,
            defaults={"role": invitation.role or "Collaborator"},
        )


@login_required
def my_projects(request):
    return render(
        request,
        "projects/list.html",
        {
            "projects": Project.objects.filter(memberships__user=request.user).select_related("idea", "owner__profile").distinct(),
            "incoming": Invitation.objects.filter(
                invitee=request.user, source=Invitation.Source.INVITATION
            ).select_related("idea__owner__profile"),
            "applications": Invitation.objects.filter(
                idea__owner=request.user, source=Invitation.Source.APPLICATION
            ).select_related("idea", "invitee__profile"),
            "ready_ideas": Idea.objects.filter(owner=request.user, project__isnull=True, invitations__status=Invitation.Status.ACCEPTED).distinct(),
        },
    )


@login_required
def respond_invitation(request, pk, decision):
    if request.method != "POST" or decision not in ("accept", "decline"):
        return redirect("projects:list")
    invitation = get_object_or_404(Invitation.objects.select_related("idea"), pk=pk, status=Invitation.Status.PENDING)
    if invitation.source == Invitation.Source.INVITATION:
        allowed = request.user == invitation.invitee
    else:
        allowed = request.user == invitation.idea.owner
    if not allowed:
        return HttpResponseForbidden("You cannot respond to this request.")
    invitation.status = Invitation.Status.ACCEPTED if decision == "accept" else Invitation.Status.DECLINED
    invitation.responded_at = timezone.now()
    invitation.save(update_fields=["status", "responded_at"])
    if invitation.status == Invitation.Status.ACCEPTED:
        try:
            project = invitation.idea.project
        except Project.DoesNotExist:
            project = None
        if project:
            _ensure_membership(project, invitation)
        messages.success(request, "Collaboration request accepted.")
    else:
        messages.info(request, "Collaboration request declined.")
    return redirect("projects:list")


@login_required
def activate_project(request, idea_pk):
    if request.method != "POST":
        return redirect("ideas:detail", pk=idea_pk)
    idea = get_object_or_404(Idea, pk=idea_pk, owner=request.user)
    accepted = idea.invitations.filter(status=Invitation.Status.ACCEPTED)
    if not accepted.exists():
        messages.error(request, "At least one collaborator must accept before you open a workspace.")
        return redirect(idea)
    project, created = Project.objects.get_or_create(idea=idea, defaults={"owner": request.user})
    ProjectMembership.objects.get_or_create(project=project, user=request.user, defaults={"role": "Project owner", "is_owner": True})
    for invitation in accepted:
        _ensure_membership(project, invitation)
    if idea.status != Idea.Status.IN_PROGRESS:
        idea.status = Idea.Status.IN_PROGRESS
        idea.save(update_fields=["status", "updated_at"])
    if created:
        messages.success(request, "Your project workspace is ready.")
    return redirect("projects:workspace", pk=project.pk)


def _member_project(request, pk):
    project = get_object_or_404(Project.objects.select_related("idea", "owner__profile"), pk=pk)
    if not project.is_member(request.user):
        return project, HttpResponseForbidden("This workspace is only available to project team members.")
    return project, None


@login_required
def workspace(request, pk):
    project, forbidden = _member_project(request, pk)
    if forbidden:
        return forbidden
    tasks = project.tasks.select_related("assignee__profile", "created_by__profile")
    columns = [(value, label, tasks.filter(status=value)) for value, label in Task.Status.choices]
    return render(
        request,
        "projects/workspace.html",
        {
            "project": project,
            "columns": columns,
            "memberships": project.memberships.select_related("user__profile"),
            "discussion": project.messages.select_related("author__profile"),
            "message_form": MessageForm(),
        },
    )


@login_required
def task_create(request, pk):
    project, forbidden = _member_project(request, pk)
    if forbidden:
        return forbidden
    if project.status == Project.Status.COMPLETED:
        messages.error(request, "Completed projects cannot receive new tasks.")
        return redirect("projects:workspace", pk=pk)
    form = TaskForm(request.POST or None, project=project)
    if request.method == "POST" and form.is_valid():
        task = form.save(commit=False)
        task.project = project
        task.created_by = request.user
        task.save()
        messages.success(request, "Task added to the board.")
        return redirect("projects:workspace", pk=pk)
    return render(request, "projects/task_form.html", {"form": form, "project": project, "heading": "Add a task"})


@login_required
def task_edit(request, pk):
    task = get_object_or_404(Task.objects.select_related("project"), pk=pk)
    if not task.project.is_member(request.user):
        return HttpResponseForbidden("This workspace is only available to project team members.")
    if not task.can_manage(request.user):
        return HttpResponseForbidden("Only the project owner, task creator, or assignee can edit this task.")
    if task.project.status == Project.Status.COMPLETED:
        messages.error(request, "Completed projects are read-only.")
        return redirect("projects:workspace", pk=task.project_id)
    form = TaskForm(request.POST or None, instance=task, project=task.project)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Task updated.")
        return redirect("projects:workspace", pk=task.project_id)
    return render(request, "projects/task_form.html", {"form": form, "project": task.project, "heading": "Edit task"})


@login_required
def task_status(request, pk):
    task = get_object_or_404(Task.objects.select_related("project"), pk=pk)
    if request.method != "POST":
        return redirect("projects:workspace", pk=task.project_id)
    if not task.project.is_member(request.user) or not task.can_manage(request.user):
        return HttpResponseForbidden("You cannot move this task.")
    status = request.POST.get("status")
    if task.project.status != Project.Status.COMPLETED and status in Task.Status.values:
        task.status = status
        task.save(update_fields=["status", "updated_at"])
        messages.success(request, "Task moved.")
    return redirect("projects:workspace", pk=task.project_id)


@login_required
def add_message(request, pk):
    project, forbidden = _member_project(request, pk)
    if forbidden:
        return forbidden
    if request.method == "POST":
        form = MessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.project = project
            message.author = request.user
            message.save()
            messages.success(request, "Message posted.")
        else:
            messages.error(request, "Write a message before posting.")
    return redirect("projects:workspace", pk=pk)


@login_required
def complete_project(request, pk):
    project = get_object_or_404(Project, pk=pk, owner=request.user)
    if request.method == "POST" and project.status != Project.Status.COMPLETED:
        project.status = Project.Status.COMPLETED
        project.completed_at = timezone.now()
        project.save(update_fields=["status", "completed_at"])
        project.idea.status = Idea.Status.COMPLETED
        project.idea.save(update_fields=["status", "updated_at"])
        messages.success(request, "Project completed. Add showcase details when you are ready to publish it.")
        return redirect("showcase:publish", project_pk=project.pk)
    return redirect("projects:workspace", pk=pk)
