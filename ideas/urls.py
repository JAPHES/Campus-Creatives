from django.urls import path

from . import views

app_name = "ideas"

urlpatterns = [
    path("", views.idea_list, name="list"),
    path("new/", views.idea_create, name="create"),
    path("<int:pk>/", views.idea_detail, name="detail"),
    path("<int:pk>/apply/", views.apply_to_idea, name="apply"),
    path("<int:pk>/invite/<int:profile_pk>/", views.invite_creative, name="invite"),
]
