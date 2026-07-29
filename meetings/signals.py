from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils import timezone
from .models import Meeting, Attendance
from communications.models import Notification
from members.models import Member

@receiver(post_save, sender=Meeting)
def meeting_saved(sender, instance, created, **kwargs):
    """Handle meeting creation and updates"""
    if created:
        # Send notification to all members
        for member in Member.objects.filter(status='active'):
            Notification.objects.create(
                recipient=member.user,
                notification_type='meeting_reminder',
                title=f'New Meeting: {instance.title}',
                message=f'Meeting scheduled for {instance.date.strftime("%B %d, %Y at %H:%M")} at {instance.venue}',
                action_url=f'/meetings/{instance.id}/'
            )
    elif instance.status == 'cancelled':
        # Notify members about cancellation
        for member in Member.objects.filter(status='active'):
            Notification.objects.create(
                recipient=member.user,
                notification_type='meeting_reminder',
                title=f'Meeting Cancelled: {instance.title}',
                message=f'The meeting scheduled for {instance.date.strftime("%B %d, %Y")} has been cancelled.',
                action_url=f'/meetings/'
            )

@receiver(post_save, sender=Attendance)
def attendance_saved(sender, instance, created, **kwargs):
    """Handle attendance recording"""
    if created and instance.status == 'present':
        # Update member compliance
        from compliance.models import ComplianceScore
        try:
            compliance = ComplianceScore.objects.get(member=instance.member)
            if compliance.score < 100:
                compliance.score = min(100, compliance.score + 2)
                compliance.save()
                compliance.update_status()
        except ComplianceScore.DoesNotExist:
            pass
        
        # Create notification
        Notification.objects.create(
            recipient=instance.member.user,
            notification_type='attendance_alert',
            title='Attendance Recorded',
            message=f'Your attendance for {instance.meeting.title} has been recorded.',
            action_url=f'/meetings/{instance.meeting.id}/'
        )
