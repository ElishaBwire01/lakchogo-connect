"""
Celery configuration for LakChogo Connect.

This file configures Celery for background task processing.
To start Celery worker: celery -A lakchogo worker -l info
To start Celery beat: celery -A lakchogo beat -l info
"""

import os
from celery import Celery
from celery.schedules import crontab

# Set default Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lakchogo.settings')

# Create Celery app
app = Celery('lakchogo')

# Load task modules from all registered Django app configs
app.config_from_object('django.conf:settings', namespace='CELERY')

# Auto-discover tasks in all installed apps
app.autodiscover_tasks()

# Beat schedule (scheduled tasks)
app.conf.beat_schedule = {
    'check-compliance-daily': {
        'task': 'compliance.tasks.check_compliance',
        'schedule': crontab(hour=0, minute=0),  # Every day at midnight
    },
    'send-meeting-reminders': {
        'task': 'meetings.tasks.send_meeting_reminders',
        'schedule': crontab(hour=8, minute=0),  # Every day at 8 AM
    },
    'check-payment-overdue': {
        'task': 'finance.tasks.check_overdue_payments',
        'schedule': crontab(hour=6, minute=0),  # Every day at 6 AM
    },
    'send-newsletter': {
        'task': 'communications.tasks.send_newsletter',
        'schedule': crontab(day_of_week='monday', hour=9, minute=0),  # Every Monday at 9 AM
    },
}

@app.task(bind=True)
def debug_task(self):
    """Debug task for testing Celery"""
    print(f'Request: {self.request!r}')
