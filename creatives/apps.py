from django.apps import AppConfig


class CreativesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "creatives"

    def ready(self):
        import creatives.signals  # noqa: F401
