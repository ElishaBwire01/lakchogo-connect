from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Report
from communications.services import NotificationTriggers

@receiver(post_save, sender=Report)
def report_saved(sender, instance, created, **kwargs):
    """Handle report save and trigger notifications"""
    if not created and instance.status == 'completed':
        # Report completed
        NotificationTriggers.report_generated(instance)
