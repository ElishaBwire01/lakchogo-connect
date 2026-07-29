from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from .models import Meeting
from .services import MeetingService

@shared_task
def send_meeting_reminders():
    """Send reminders for upcoming meetings"""
    upcoming = Meeting.objects.filter(
        date__gte=timezone.now(),
        date__lte=timezone.now() + timedelta(days=1),
        status='scheduled'
    )
    
    for meeting in upcoming:
        MeetingService.send_meeting_reminders(meeting)
    
    return f"Sent reminders for {upcoming.count()} meetings"

@shared_task
def auto_complete_meetings():
    """Auto-complete meetings that have passed"""
    passed = Meeting.objects.filter(
        date__lt=timezone.now() - timedelta(hours=2),
        status='scheduled'
    )
    
    for meeting in passed:
        meeting.status = 'completed'
        meeting.save()
    
    return f"Completed {passed.count()} meetings"

@shared_task
def generate_attendance_report(meeting_id):
    """Generate attendance report for a meeting"""
    from reports.generators.attendance_report import generate_report
    from meetings.models import Meeting
    
    meeting = Meeting.objects.get(id=meeting_id)
    return generate_report(meeting)
