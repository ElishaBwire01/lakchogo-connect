from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils import timezone
from .models import Meeting, Attendance
from communications.services import NotificationTriggers

@receiver(post_save, sender=Meeting)
def meeting_saved(sender, instance, created, **kwargs):
    """Handle meeting save and trigger notifications"""
    if created:
        # Meeting created - send notifications
        try:
            NotificationTriggers.meeting_scheduled(instance)
        except Exception as e:
            print(f"Error sending meeting notifications: {e}")
    
    # Check if status changed to cancelled
    if hasattr(instance, '_status_before'):
        if instance._status_before != 'cancelled' and instance.status == 'cancelled':
            try:
                NotificationTriggers.meeting_cancelled(instance)
            except Exception as e:
                print(f"Error sending cancellation notifications: {e}")

@receiver(pre_save, sender=Meeting)
def meeting_pre_save(sender, instance, **kwargs):
    """Store previous status before save"""
    if instance.pk:
        try:
            old = Meeting.objects.get(pk=instance.pk)
            instance._status_before = old.status
        except Meeting.DoesNotExist:
            pass

@receiver(post_save, sender=Attendance)
def attendance_saved(sender, instance, created, **kwargs):
    """Handle attendance save and trigger notifications"""
    if created and instance.status == 'present':
        try:
            NotificationTriggers.attendance_recorded(instance)
        except Exception as e:
            print(f"Error sending attendance notification: {e}")
        
        # Update compliance
        from compliance.services import ComplianceService
        try:
            ComplianceService.check_member(instance.member)
        except Exception as e:
            print(f"Error updating compliance for {instance.member}: {e}")
