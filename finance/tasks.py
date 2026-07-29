from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from .models import Payment, PaymentCategory, PaymentReminder
from members.models import Member
from communications.models import Notification

@shared_task
def check_overdue_payments():
    """Check and create reminders for overdue payments"""
    members = Member.objects.filter(status='active')
    reminders_created = 0
    
    for member in members:
        categories = PaymentCategory.objects.filter(is_active=True)
        
        for category in categories:
            last_payment = Payment.objects.filter(
                member=member,
                category=category,
                status='completed'
            ).order_by('-created_at').first()
            
            if not last_payment:
                # No payment ever made
                PaymentReminder.objects.create(
                    member=member,
                    category=category,
                    reminder_type='overdue',
                    message=f'Please make your payment for {category.name}. No payments recorded yet.'
                )
                reminders_created += 1
            elif last_payment.created_at < timezone.now() - timedelta(days=30):
                # Payment overdue
                days = (timezone.now() - last_payment.created_at).days
                PaymentReminder.objects.create(
                    member=member,
                    category=category,
                    reminder_type='overdue',
                    message=f'Your payment for {category.name} is overdue by {days} days.'
                )
                reminders_created += 1
    
    return f"Created {reminders_created} reminders"

@shared_task
def send_payment_reminders():
    """Send payment reminders to members"""
    reminders = PaymentReminder.objects.filter(is_read=False)
    
    for reminder in reminders:
        Notification.objects.create(
            recipient=reminder.member.user,
            notification_type='payment_reminder',
            title=f'Payment Reminder: {reminder.reminder_type}',
            message=reminder.message,
            action_url='/finance/payments/'
        )
        reminder.is_read = True
        reminder.save()
    
    return f"Sent {reminders.count()} reminders"

@shared_task
def generate_monthly_report():
    """Generate monthly payment report"""
    from reports.generators.financial_report import generate_monthly_report
    return generate_monthly_report()
