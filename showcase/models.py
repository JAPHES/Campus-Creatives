from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator, MaxValueValidator, MinValueValidator
from django.db import models

from projects.models import Project, ProjectMembership


class ShowcaseEntry(models.Model):
    project = models.OneToOneField(Project, on_delete=models.PROTECT, related_name="showcase_entry")
    title = models.CharField(max_length=180)
    description = models.TextField(max_length=3000)
    cover_image = models.ImageField(
        upload_to="showcase/%Y/%m/",
        blank=True,
        validators=[FileExtensionValidator(["jpg", "jpeg", "png", "webp"])],
    )
    media_link = models.URLField(blank=True, help_text="Optional link to the finished work.")
    is_published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    published_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ("-published_at", "-created_at")

    def __str__(self):
        return self.title

    def clean(self):
        if self.project_id and self.project.status != Project.Status.COMPLETED:
            raise ValidationError("Only completed projects can be added to the showcase.")


class ShowcaseCredit(models.Model):
    entry = models.ForeignKey(ShowcaseEntry, on_delete=models.CASCADE, related_name="credits")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="showcase_credits")
    role = models.CharField(max_length=100)

    class Meta:
        ordering = ("id",)
        constraints = [models.UniqueConstraint(fields=("entry", "user"), name="unique_showcase_credit")]

    def __str__(self):
        return f"{self.user} — {self.role}"


class Rating(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="ratings")
    rater = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="ratings_given")
    rated_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="ratings_received")
    score = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.CharField(max_length=400, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-created_at",)
        constraints = [
            models.UniqueConstraint(fields=("project", "rater", "rated_user"), name="one_rating_per_teammate_project")
        ]

    def __str__(self):
        return f"{self.rater} rated {self.rated_user}: {self.score}"

    def clean(self):
        errors = {}
        if self.rater_id is not None and self.rated_user_id is not None and self.rater_id == self.rated_user_id:
            errors["rated_user"] = "You cannot rate yourself."
        if self.project_id:
            if self.project.status != Project.Status.COMPLETED:
                errors["project"] = "Ratings are available after project completion."
            member_ids = set(ProjectMembership.objects.filter(project=self.project).values_list("user_id", flat=True))
            if self.rater_id not in member_ids or self.rated_user_id not in member_ids:
                errors["rated_user"] = "Both people must be members of this project."
        if errors:
            raise ValidationError(errors)
