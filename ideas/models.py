from django.conf import settings
from django.db import models
from django.urls import reverse

from creatives.models import Campus, Skill


class Idea(models.Model):
    class BudgetType(models.TextChoices):
        PAID = "paid", "Paid"
        FREE = "free", "Free collaboration"
        REVENUE_SHARE = "revenue_share", "Revenue share"

    class Status(models.TextChoices):
        OPEN = "open", "Open"
        IN_PROGRESS = "in_progress", "In progress"
        COMPLETED = "completed", "Completed"

    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="ideas")
    title = models.CharField(max_length=160)
    description = models.TextField(max_length=3000)
    campus = models.ForeignKey(Campus, on_delete=models.PROTECT, related_name="ideas")
    skills_needed = models.ManyToManyField(Skill, related_name="ideas")
    budget_type = models.CharField(max_length=30, choices=BudgetType.choices)
    budget_details = models.CharField(max_length=240, blank=True)
    deadline = models.DateField()
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.OPEN)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-created_at",)
        indexes = [models.Index(fields=["status", "-created_at"]), models.Index(fields=["campus", "status"])]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("ideas:detail", kwargs={"pk": self.pk})
