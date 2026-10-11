from django.urls import path

from . import views

app_name = "projects"

urlpatterns = [
    path("", views.my_projects, name="list"),
    path("invitations/<int:pk>/<str:decision>/", views.respond_invitation, name="respond"),
    path("activate/<int:idea_pk>/", views.activate_project, name="activate"),
    path("<int:pk>/", views.workspace, name="workspace"),
    path("<int:pk>/tasks/new/", views.task_create, name="task_create"),
    path("tasks/<int:pk>/edit/", views.task_edit, name="task_edit"),
    path("tasks/<int:pk>/status/", views.task_status, name="task_status"),
    path("<int:pk>/messages/", views.add_message, name="message"),
    path("<int:pk>/complete/", views.complete_project, name="complete"),
]
