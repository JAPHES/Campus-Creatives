from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("accounts.urls")),
    path("creatives/", include("creatives.urls")),
    path("ideas/", include("ideas.urls")),
    path("projects/", include("projects.urls")),
    path("showcase/", include("showcase.urls")),
    path("", include("core.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

admin.site.site_header = "Campus Creatives administration"
admin.site.site_title = "Campus Creatives admin"
admin.site.index_title = "Manage the community"
