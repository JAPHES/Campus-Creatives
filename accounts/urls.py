from django.urls import path

from . import views

app_name = "accounts"

urlpatterns = [
    path("register/", views.register, name="register"),
    path("login/", views.EmailLoginView.as_view(), name="login"),
    path("logout/", views.AccountLogoutView.as_view(), name="logout"),
    path("settings/", views.settings_view, name="settings"),
]
