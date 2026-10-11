from django import forms

from .models import DiscussionMessage, ProjectMembership, Task


class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ("title", "description", "assignee", "due_date", "status")
        widgets = {
            "description": forms.Textarea(attrs={"rows": 4}),
            "due_date": forms.DateInput(attrs={"type": "date"}),
        }

    def __init__(self, *args, project=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.project = project
        if project:
            self.fields["assignee"].queryset = type(project.owner).objects.filter(project_memberships__project=project).distinct()
            self.fields["assignee"].label_from_instance = lambda user: user.profile.name

    def clean_assignee(self):
        assignee = self.cleaned_data.get("assignee")
        if assignee and self.project and not ProjectMembership.objects.filter(project=self.project, user=assignee).exists():
            raise forms.ValidationError("Choose a member of this project.")
        return assignee


class MessageForm(forms.ModelForm):
    class Meta:
        model = DiscussionMessage
        fields = ("body",)
        labels = {"body": "Message"}
        widgets = {"body": forms.Textarea(attrs={"rows": 3, "placeholder": "Share an update with the team…"})}
