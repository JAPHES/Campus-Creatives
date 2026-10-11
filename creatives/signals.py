from django.core.exceptions import ValidationError
from django.db.models.signals import m2m_changed
from django.dispatch import receiver

from .models import CreativeProfile


@receiver(m2m_changed, sender=CreativeProfile.skills.through)
def enforce_three_skill_limit(sender, instance, action, reverse, pk_set, **kwargs):
    if action != "pre_add":
        return
    if reverse:
        for profile in CreativeProfile.objects.filter(pk__in=pk_set):
            if profile.skills.count() >= 3:
                raise ValidationError(f"{profile.name} already has the maximum of three skills.")
    elif instance.skills.count() + len(pk_set) > 3:
        raise ValidationError("A creative profile can have no more than three skills.")
