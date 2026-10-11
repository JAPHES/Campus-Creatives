from django.conf import settings
from django.core.validators import FileExtensionValidator
from django.db import models
from django.urls import reverse
from django.utils.text import slugify


class Campus(models.Model):
    name = models.CharField(max_length=180, unique=True)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ("name",)
        verbose_name_plural = "campuses"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Skill(models.Model):
    name = models.CharField(max_length=80, unique=True)
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    category = models.CharField(max_length=80, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ("category", "name")

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class CreativeProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile")
    name = models.CharField(max_length=120)
    bio = models.TextField(max_length=500, blank=True)
    campus = models.ForeignKey(Campus, on_delete=models.SET_NULL, null=True, blank=True, related_name="creatives")
    skills = models.ManyToManyField(Skill, blank=True, related_name="creatives")
    whatsapp_number = models.CharField(max_length=30, blank=True)
    show_whatsapp = models.BooleanField(default=False, help_text="Show my WhatsApp number on my public profile.")
    is_available = models.BooleanField(default=True, verbose_name="Available for collaboration")
    photo = models.ImageField(
        upload_to="profiles/%Y/%m/",
        blank=True,
        validators=[FileExtensionValidator(["jpg", "jpeg", "png", "webp"])],
    )
    is_verified = models.BooleanField(default=False, help_text="Managed by an administrator.")
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("name",)
        indexes = [models.Index(fields=["campus", "is_available"])]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("creatives:profile", kwargs={"pk": self.pk})


class PortfolioLink(models.Model):
    profile = models.ForeignKey(CreativeProfile, on_delete=models.CASCADE, related_name="portfolio_links")
    title = models.CharField(max_length=100)
    url = models.URLField()

    class Meta:
        ordering = ("id",)

    def __str__(self):
        return f"{self.profile.name}: {self.title}"
