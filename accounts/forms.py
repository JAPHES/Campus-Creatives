from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

from .models import User


class RegisterForm(UserCreationForm):
    name = forms.CharField(max_length=120, help_text="The name shown on your creative profile.")

    class Meta:
        model = User
        fields = ("name", "email", "password1", "password2")

    def save(self, commit=True):
        user = super().save(commit=commit)
        if commit:
            user.profile.name = self.cleaned_data["name"]
            user.profile.save(update_fields=["name"])
        return user


class EmailAuthenticationForm(AuthenticationForm):
    username = forms.EmailField(label="Email", widget=forms.EmailInput(attrs={"autofocus": True}))
