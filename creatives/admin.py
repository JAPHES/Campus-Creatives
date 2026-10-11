from django.contrib import admin

from .forms import CreativeProfileForm
from .models import Campus, CreativeProfile, PortfolioLink, Skill


@admin.register(Campus)
class CampusAdmin(admin.ModelAdmin):
    list_display = ("name", "city", "state", "is_active")
    list_filter = ("is_active", "state")
    search_fields = ("name", "city", "state")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "is_active")
    list_filter = ("category", "is_active")
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}


class PortfolioLinkInline(admin.TabularInline):
    model = PortfolioLink
    extra = 0


@admin.register(CreativeProfile)
class CreativeProfileAdmin(admin.ModelAdmin):
    form = CreativeProfileForm
    list_display = ("name", "user", "campus", "is_available", "is_verified")
    list_filter = ("is_available", "is_verified", "campus")
    search_fields = ("name", "user__email", "bio")
    filter_horizontal = ("skills",)
    inlines = (PortfolioLinkInline,)
