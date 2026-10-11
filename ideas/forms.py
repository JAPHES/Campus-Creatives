from datetime import date

from django import forms

from .models import Idea


class IdeaForm(forms.ModelForm):
    class Meta:
        model = Idea
        fields = ("title", "description", "campus", "skills_needed", "budget_type", "budget_details", "deadline")
        widgets = {
            "description": forms.Textarea(attrs={"rows": 7, "placeholder": "Describe the outcome, the audience, and what help you need."}),
            "skills_needed": forms.CheckboxSelectMultiple(),
            "deadline": forms.DateInput(attrs={"type": "date"}),
            "budget_details": forms.TextInput(attrs={"placeholder": "Optional: amount, split, or other context"}),
        }

    def clean_deadline(self):
        deadline = self.cleaned_data["deadline"]
        if deadline < date.today():
            raise forms.ValidationError("Choose today or a future date.")
        return deadline

    def clean_skills_needed(self):
        skills = self.cleaned_data["skills_needed"]
        if not skills:
            raise forms.ValidationError("Choose at least one skill.")
        return skills


class CollaborationRequestForm(forms.Form):
    role = forms.CharField(max_length=100, initial="Collaborator", help_text="For example: Designer, photographer, or editor.")
    message = forms.CharField(max_length=500, required=False, widget=forms.Textarea(attrs={"rows": 3}))
