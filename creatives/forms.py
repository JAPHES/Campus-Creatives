from django import forms
from django.forms import inlineformset_factory

from .models import CreativeProfile, PortfolioLink


class CreativeProfileForm(forms.ModelForm):
    class Meta:
        model = CreativeProfile
        fields = ("name", "bio", "campus", "skills", "is_available", "photo", "whatsapp_number", "show_whatsapp")
        widgets = {
            "bio": forms.Textarea(attrs={"rows": 4, "placeholder": "What do you create, and what would you love to work on?"}),
            "skills": forms.CheckboxSelectMultiple(),
            "whatsapp_number": forms.TextInput(attrs={"placeholder": "+234…"}),
        }
        help_texts = {"skills": "Choose up to three skills. Skills and campuses are managed by the site administrator."}

    def clean_skills(self):
        skills = self.cleaned_data["skills"]
        if len(skills) > 3:
            raise forms.ValidationError("Choose no more than three skills.")
        return skills

    def clean_photo(self):
        photo = self.cleaned_data.get("photo")
        if photo and getattr(photo, "size", 0) > 5 * 1024 * 1024:
            raise forms.ValidationError("Profile photos must be 5 MB or smaller.")
        return photo


PortfolioLinkFormSet = inlineformset_factory(
    CreativeProfile,
    PortfolioLink,
    fields=("title", "url"),
    extra=1,
    max_num=5,
    validate_max=True,
    can_delete=True,
)
