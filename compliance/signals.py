from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import ComplianceScore
from members.models import Member
from finance.models import Payment
from meetings.models import Attendance

@receiver(post_save, sender=Member)
def create_compliance_score(sender, instance, created, **kwargs):
    """Create compliance score when a new member is created"""
    if created:
        ComplianceScore.objects.get_or_create(
            member=instance,
            defaults={
                'status': 'green',
                'score': 100.00,
                'payment_compliance': 100.00,
                'attendance_compliance': 100.00
            }
        )

@receiver(post_save, sender=Payment)
def update_compliance_on_payment(sender, instance, created, **kwargs):
    """Update compliance when a payment is recorded"""
    if created and instance.status == 'completed':
        from .services import ComplianceService
        try:
            ComplianceService.check_member(instance.member)
        except Exception as e:
            # Log error but don't break the flow
            print(f"Error updating compliance for {instance.member}: {e}")

@receiver(post_save, sender=Attendance)
def update_compliance_on_attendance(sender, instance, created, **kwargs):
    """Update compliance when attendance is recorded"""
    if created or instance.status == 'present':
        from .services import ComplianceService
        try:
            ComplianceService.check_member(instance.member)
        except Exception as e:
            # Log error but don't break the flow
            print(f"Error updating compliance for {instance.member}: {e}")
