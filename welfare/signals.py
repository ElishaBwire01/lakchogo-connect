from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import BereavementEvent, BereavementContribution
from communications.services import NotificationTriggers

@receiver(post_save, sender=BereavementEvent)
def bereavement_event_saved(sender, instance, created, **kwargs):
    """Handle bereavement event save"""
    if created:
        # Event created
        NotificationTriggers.welfare_event_created(instance)

@receiver(post_save, sender=BereavementContribution)
def bereavement_contribution_saved(sender, instance, created, **kwargs):
    """Handle bereavement contribution save"""
    if created:
        # Contribution made
        NotificationTriggers.welfare_contribution_made(instance)
        
        # Update event amount collected
        event = instance.event
        event.amount_collected += instance.amount
        event.save()
        
        # Check if target reached
        if event.amount_collected >= event.collection_target:
            NotificationTriggers.welfare_target_reached(event)
