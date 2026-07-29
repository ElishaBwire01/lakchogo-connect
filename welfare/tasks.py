from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from .models import BereavementEvent
from .services import WelfareService

@shared_task
def check_events_status():
    """Check and update event statuses"""
    # Auto-close events older than 90 days
    cutoff_date = timezone.now().date() - timedelta(days=90)
    old_events = BereavementEvent.objects.filter(
        date_of_death__lt=cutoff_date,
        status='active'
    )
    
    for event in old_events:
        event.close()
    
    return f"Closed {old_events.count()} old events"

@shared_task
def send_welfare_reminders():
    """Send reminders for active events"""
    active_events = BereavementEvent.objects.filter(status='active')
    
    for event in active_events:
        if event.progress_percentage < 50:
            # Send reminder to committee
            from communications.models import Notification
            from django.contrib.auth import get_user_model
            User = get_user_model()
            
            for user in User.objects.filter(is_committee=True):
                Notification.objects.create(
                    recipient=user,
                    notification_type='welfare_alert',
                    title=f'Action Required: {event.event_code}',
                    message=f'Collection for {event.deceased_name} is at {event.progress_percentage:.0f}%. Target: KES {event.collection_target}',
                    action_url=f'/welfare/{event.id}/'
                )
    
    return f"Sent reminders for {active_events.count()} events"

@shared_task
def generate_welfare_report():
    """Generate welfare report"""
    from reports.generators.welfare_report import generate_report
    return generate_report()
