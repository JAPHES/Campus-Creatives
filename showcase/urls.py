from django.urls import path

from . import views

app_name = "showcase"

urlpatterns = [
    path("", views.showcase_list, name="list"),
    path("<int:pk>/", views.showcase_detail, name="detail"),
    path("project/<int:project_pk>/publish/", views.publish_showcase, name="publish"),
    path("<int:pk>/rate/<int:user_pk>/", views.rate_member, name="rate"),
]
