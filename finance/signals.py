from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Payment
from communications.models import Notification

@receiver(post_save, sender=Payment)
def payment_saved(sender, instance, created, **kwargs):
    """Handle payment save"""
    if created and instance.status == 'completed' and instance.member and instance.member.user:
        try:
            # Create notification for member
            Notification.objects.create(
                recipient=instance.member.user,
                notification_type='payment_reminder',
                title=f'Payment Received: {instance.category.name}',
                message=f'Your payment of KES {instance.amount} for {instance.category.name} has been recorded.',
                action_url=f'/finance/payments/{instance.id}/'
            )
            
            # Update compliance score
            from compliance.services import ComplianceService
            try:
                ComplianceService.check_member(instance.member)
            except Exception as e:
                # Log error but don't break the flow
                print(f"Error updating compliance for {instance.member}: {e}")
        except Exception as e:
            # Log error but don't break the flow
            print(f"Error creating notification for payment {instance.id}: {e}")
    
    elif created and instance.status == 'pending' and instance.recorded_by:
        try:
            # Notify treasurer
            Notification.objects.create(
                recipient=instance.recorded_by,
                notification_type='payment_reminder',
                title=f'Payment Pending: {instance.category.name}',
                message=f'Payment of KES {instance.amount} from {instance.member.get_full_name()} needs verification.',
                action_url=f'/finance/payments/{instance.id}/approve/'
            )
        except Exception as e:
            print(f"Error creating notification for pending payment {instance.id}: {e}")
