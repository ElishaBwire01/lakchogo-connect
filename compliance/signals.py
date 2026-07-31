from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import ComplianceScore
from communications.services import NotificationTriggers

@receiver(post_save, sender=ComplianceScore)
def compliance_score_saved(sender, instance, created, **kwargs):
    """Handle compliance score save and trigger notifications"""
    # Check if status changed
    if not created and hasattr(instance, '_status_before'):
        if instance._status_before != instance.status:
            NotificationTriggers.compliance_updated(instance)

@receiver(post_save, sender=ComplianceScore)
def create_alert_on_red(sender, instance, created, **kwargs):
    """Create alert when compliance is red"""
    if instance.status == 'red':
        from .models import ComplianceAlert
        alert, created = ComplianceAlert.objects.get_or_create(
            member=instance.member,
            is_resolved=False,
            defaults={
                'alert_type': 'compliance_low',
                'priority': 'high',
                'message': f'Compliance score is {instance.score}%. Action required.'
            }
        )
        if not created:
            alert.message = f'Compliance score is {instance.score}%. Action required.'
            alert.save()
