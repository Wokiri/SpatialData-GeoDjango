from .models import (
    User, LandOwner
)

from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=User)
def post_save_adjustments(sender, instance, created, **kwargs):
    if created:
        LandOwner.objects.create(user=instance)