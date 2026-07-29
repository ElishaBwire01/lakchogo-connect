from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import BereavementEvent, BereavementContribution
from .services import WelfareService

@receiver(post_save, sender=BereavementEvent)
def bereavement_event_saved(sender, instance, created, **kwargs):
    """Handle bereavement event save"""
    if created:
        # Send notifications
        WelfareService.notify_event_created(instance)

@receiver(post_save, sender=BereavementContribution)
def bereavement_contribution_saved(sender, instance, created, **kwargs):
    """Handle bereavement contribution save"""
    if created:
        # Update event amount collected
        event = instance.event
        event.amount_collected += instance.amount
        event.save()
        
        # Check if target reached
        if event.amount_collected >= event.collection_target:
            WelfareService.notify_target_reached(event)
