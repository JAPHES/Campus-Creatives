from django import forms

from .models import Rating, ShowcaseEntry


class ShowcaseForm(forms.ModelForm):
    class Meta:
        model = ShowcaseEntry
        fields = ("title", "description", "cover_image", "media_link")
        widgets = {"description": forms.Textarea(attrs={"rows": 7})}

    def clean_cover_image(self):
        image = self.cleaned_data.get("cover_image")
        if image and getattr(image, "size", 0) > 5 * 1024 * 1024:
            raise forms.ValidationError("Cover images must be 5 MB or smaller.")
        return image


class RatingForm(forms.ModelForm):
    class Meta:
        model = Rating
        fields = ("score", "comment")
        widgets = {
            "score": forms.Select(choices=[(number, f"{number} — " + label) for number, label in [(1, "Needs improvement"), (2, "Fair"), (3, "Good"), (4, "Great"), (5, "Excellent")]]),
            "comment": forms.Textarea(attrs={"rows": 4, "placeholder": "Share brief, constructive feedback."}),
        }
