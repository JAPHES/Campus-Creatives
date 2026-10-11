from django.contrib import admin

from .models import Report


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ("subject", "reporter", "status", "created_at")
    list_filter = ("status", "created_at")
    search_fields = ("subject", "details", "reporter__email")
