from django.contrib import admin

from .models import Rating, ShowcaseCredit, ShowcaseEntry


class CreditInline(admin.TabularInline):
    model = ShowcaseCredit
    extra = 0


@admin.register(ShowcaseEntry)
class ShowcaseEntryAdmin(admin.ModelAdmin):
    list_display = ("title", "project", "is_published", "published_at")
    list_filter = ("is_published", "published_at")
    search_fields = ("title", "description", "project__idea__title")
    inlines = (CreditInline,)


@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    list_display = ("project", "rater", "rated_user", "score", "created_at")
    list_filter = ("score", "created_at")
    search_fields = ("project__idea__title", "rater__email", "rated_user__email", "comment")
