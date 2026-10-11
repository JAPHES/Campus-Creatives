from django.contrib import admin

from .models import Idea


@admin.register(Idea)
class IdeaAdmin(admin.ModelAdmin):
    list_display = ("title", "owner", "campus", "budget_type", "status", "deadline", "created_at")
    list_filter = ("status", "budget_type", "campus", "created_at")
    search_fields = ("title", "description", "owner__email")
    filter_horizontal = ("skills_needed",)
    readonly_fields = ("created_at", "updated_at")
