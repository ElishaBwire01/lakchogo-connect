from celery import shared_task
from django.utils import timezone
from .services import ComplianceService

@shared_task
def run_daily_compliance_check():
    """Run compliance check for all members daily"""
    result = ComplianceService.check_all_members()
    return {
        'status': 'success',
        'total_checked': result['total'],
        'updated': result['updated'],
        'timestamp': timezone.now().isoformat()
    }

@shared_task
def send_compliance_alerts():
    """Send compliance alerts to members"""
    from communications.models import Notification
    from .models import ComplianceAlert, ComplianceScore
    
    # Get members with low compliance
    scores = ComplianceScore.objects.filter(status='red')
    
    for score in scores:
        # Create notification
        Notification.objects.create(
            recipient=score.member.user,
            notification_type='compliance_alert',
            title='⚠️ Compliance Warning',
            message=f'Your compliance score is {score.score}%. Please take action to restore eligibility.',
            action_url=f'/compliance/member/{score.member.member_id}/'
        )
        
        # Create alert if not exists
        alert, created = ComplianceAlert.objects.get_or_create(
            member=score.member,
            alert_type='compliance_low',
            is_resolved=False,
            defaults={
                'priority': 'high',
                'message': f'Compliance score is {score.score}%. Action required.'
            }
        )
        
        if not created:
            alert.message = f'Compliance score is {score.score}%. Action required.'
            alert.save()
    
    return f"Sent alerts for {scores.count()} members"
