from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Payment
from communications.services import NotificationTriggers

@receiver(post_save, sender=Payment)
def payment_saved(sender, instance, created, **kwargs):
    """Handle payment save and trigger notifications"""
    if created:
        # Payment created
        NotificationTriggers.payment_created(instance)
        
        # Update compliance
        from compliance.services import ComplianceService
        try:
            ComplianceService.check_member(instance.member)
        except Exception as e:
            print(f"Error updating compliance for {instance.member}: {e}")
    
    # Check if status changed to approved
    if hasattr(instance, '_status_before'):
        if instance._status_before == 'pending' and instance.status == 'completed':
            NotificationTriggers.payment_approved(instance)
