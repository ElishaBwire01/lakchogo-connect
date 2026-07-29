from django.utils import timezone
from django.db.models import Sum, Count, Q
from .models import BereavementEvent, BereavementContribution, WelfareFund
from members.models import Member

class WelfareService:
    """Service layer for welfare operations"""
    
    @staticmethod
    def get_welfare_stats():
        """Get welfare statistics"""
        total_events = BereavementEvent.objects.count()
        active_events = BereavementEvent.objects.filter(status='active').count()
        total_collected = BereavementEvent.objects.aggregate(
            total=Sum('amount_collected')
        )['total'] or 0
        
        total_disbursed = BereavementEvent.objects.aggregate(
            total=Sum('amount_disbursed')
        )['total'] or 0
        
        return {
            'total_events': total_events,
            'active_events': active_events,
            'total_collected': total_collected,
            'total_disbursed': total_disbursed,
            'available_balance': total_collected - total_disbursed,
        }
    
    @staticmethod
    def get_event_details(event_id):
        """Get detailed event information"""
        try:
            event = BereavementEvent.objects.get(id=event_id)
            contributions = event.contributions.all()
            
            return {
                'event': event,
                'total_contributors': contributions.values('contributor').distinct().count(),
                'total_contributions': contributions.count(),
                'progress': event.progress_percentage,
                'remaining': event.collection_target - event.amount_collected,
                'top_contributors': contributions.order_by('-amount')[:5],
            }
        except BereavementEvent.DoesNotExist:
            return None
    
    @staticmethod
    def get_member_contributions(member):
        """Get all contributions by a member"""
        return BereavementContribution.objects.filter(
            contributor=member
        ).select_related('event').order_by('-created_at')
    
    @staticmethod
    def get_fund_summary():
        """Get welfare fund summary"""
        funds = WelfareFund.objects.filter(is_active=True)
        
        return {
            'total_balance': funds.aggregate(total=Sum('balance'))['total'] or 0,
            'funds': funds,
        }
    
    @staticmethod
    def calculate_bereaverment_share(event):
        """Calculate each member's share for a bereavement event"""
        active_members = Member.objects.filter(status='active').count()
        if active_members > 0:
            return event.collection_target / active_members
        return 0
    
    @staticmethod
    def notify_event_created(event):
        """Send notifications when a bereavement event is created"""
        from communications.models import Notification
        
        members = Member.objects.filter(status='active')
        for member in members:
            Notification.objects.create(
                recipient=member.user,
                notification_type='welfare_alert',
                title=f'Bereavement Event: {event.deceased_name}',
                message=f'A bereavement event has been created for {event.member.get_full_name()}. Target: KES {event.collection_target}',
                action_url=f'/welfare/{event.id}/'
            )
    
    @staticmethod
    def notify_target_reached(event):
        """Send notifications when collection target is reached"""
        from communications.models import Notification
        
        members = Member.objects.filter(status='active')
        for member in members:
            Notification.objects.create(
                recipient=member.user,
                notification_type='welfare_alert',
                title=f'Collection Target Reached!',
                message=f'The collection target for {event.deceased_name} has been reached. Amount: KES {event.amount_collected}',
                action_url=f'/welfare/{event.id}/'
            )
