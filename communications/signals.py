from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Notification

@receiver(post_save, sender=Notification)
def notification_saved(sender, instance, created, **kwargs):
    """Handle notification save"""
    if created:
        # Auto-mark as sent if channel is in_app
        if instance.channel == 'in_app':
            instance.mark_as_sent()
