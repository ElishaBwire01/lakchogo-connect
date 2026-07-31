from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Member, MemberContributionSummary
from communications.services import NotificationTriggers
from compliance.models import ComplianceScore

@receiver(post_save, sender=Member)
def member_saved(sender, instance, created, **kwargs):
    """Handle member save and trigger notifications"""
    if created:
        # Member registered
        NotificationTriggers.member_registered(instance)
        
        # Create compliance score
        ComplianceScore.objects.get_or_create(
            member=instance,
            defaults={
                'status': 'green',
                'score': 100.00
            }
        )

@receiver(post_save, sender=MemberContributionSummary)
def contribution_summary_saved(sender, instance, created, **kwargs):
    """Handle contribution summary update"""
    # This could trigger notifications for low balance
    if instance.balance > 1000:
        # Send reminder if balance is high
        from communications.services import NotificationService
        NotificationService.send_notification(
            user=instance.member.user,
            notification_type='payment_reminder',
            title='💳 Payment Reminder',
            message=f'Your balance is KES {instance.balance}. Please make your payment.',
            action_url=f'/finance/payments/'
        )
