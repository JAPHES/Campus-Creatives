from django.urls import path

from . import views

app_name = "creatives"

urlpatterns = [
    path("", views.creative_list, name="list"),
    path("<int:pk>/", views.profile_detail, name="profile"),
]
