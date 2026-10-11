from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import redirect, render

from creatives.forms import CreativeProfileForm, PortfolioLinkFormSet

from .forms import EmailAuthenticationForm, RegisterForm


class EmailLoginView(LoginView):
    authentication_form = EmailAuthenticationForm
    template_name = "accounts/login.html"


class AccountLogoutView(LogoutView):
    http_method_names = ["post"]


def register(request):
    if request.user.is_authenticated:
        return redirect("core:dashboard")
    form = RegisterForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        login(request, user)
        messages.success(request, "Welcome to Campus Creatives. Complete your profile to get started.")
        return redirect("accounts:settings")
    return render(request, "accounts/register.html", {"form": form})


@login_required
def settings_view(request):
    profile = request.user.profile
    form = CreativeProfileForm(request.POST or None, request.FILES or None, instance=profile)
    formset = PortfolioLinkFormSet(request.POST or None, instance=profile, prefix="portfolio")
    if request.method == "POST" and form.is_valid() and formset.is_valid():
        form.save()
        formset.save()
        messages.success(request, "Your creative profile has been updated.")
        return redirect("creatives:profile", pk=profile.pk)
    return render(request, "accounts/settings.html", {"form": form, "formset": formset})
