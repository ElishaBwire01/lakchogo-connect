from django.db.models import Count, Sum, Q
from django.utils import timezone
from datetime import datetime, timedelta
from django.contrib.auth import get_user_model
from members.models import Member
from finance.models import Payment
from meetings.models import Meeting, Attendance
from compliance.models import ComplianceScore

User = get_user_model()

class DashboardService:
    """Service for dashboard data aggregation"""
    
    @staticmethod
    def get_member_stats():
        """Get member statistics"""
        total_members = Member.objects.filter(status='active').count()
        new_members = Member.objects.filter(
            date_joined__gte=timezone.now() - timedelta(days=30)
        ).count()
        active_members = Member.objects.filter(
            status='active'
        ).count()
        
        return {
            'total': total_members,
            'new': new_members,
            'active': active_members,
            'inactive': Member.objects.filter(status='inactive').count(),
        }
    
    @staticmethod
    def get_payment_stats():
        """Get payment statistics"""
        total_payments = Payment.objects.filter(
            status='completed'
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        pending_payments = Payment.objects.filter(
            status='pending'
        ).count()
        
        monthly_payments = Payment.objects.filter(
            status='completed',
            created_at__gte=timezone.now() - timedelta(days=30)
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        return {
            'total': total_payments,
            'pending': pending_payments,
            'monthly': monthly_payments,
            'count': Payment.objects.filter(status='completed').count(),
        }
    
    @staticmethod
    def get_meeting_stats():
        """Get meeting statistics"""
        total_meetings = Meeting.objects.count()
        upcoming_meetings = Meeting.objects.filter(
            date__gte=timezone.now(),
            status='scheduled'
        ).count()
        
        today_meetings = Meeting.objects.filter(
            date__date=timezone.now().date(),
            status__in=['scheduled', 'ongoing']
        ).count()
        
        return {
            'total': total_meetings,
            'upcoming': upcoming_meetings,
            'today': today_meetings,
        }
    
    @staticmethod
    def get_compliance_stats():
        """Get compliance statistics"""
        green = ComplianceScore.objects.filter(status='green').count()
        yellow = ComplianceScore.objects.filter(status='yellow').count()
        red = ComplianceScore.objects.filter(status='red').count()
        
        return {
            'green': green,
            'yellow': yellow,
            'red': red,
            'total': green + yellow + red,
        }
    
    @staticmethod
    def get_recent_activity(limit=10):
        """Get recent system activity"""
        recent_activities = []
        
        # Recent members
        recent_members = Member.objects.filter(
            status='active'
        ).order_by('-date_joined')[:3]
        
        for member in recent_members:
            recent_activities.append({
                'type': 'member',
                'message': f'New member registered: {member.get_full_name()}',
                'time': member.date_joined,
                'icon': 'user-plus',
                'color': 'success',
            })
        
        # Recent payments
        recent_payments = Payment.objects.filter(
            status='completed'
        ).order_by('-created_at')[:3]
        
        for payment in recent_payments:
            recent_activities.append({
                'type': 'payment',
                'message': f'Payment of KES {payment.amount} received from {payment.member.get_full_name()}',
                'time': payment.created_at,
                'icon': 'credit-card',
                'color': 'primary',
            })
        
        # Recent meetings
        recent_meetings = Meeting.objects.order_by('-created_at')[:3]
        
        for meeting in recent_meetings:
            recent_activities.append({
                'type': 'meeting',
                'message': f'Meeting scheduled: {meeting.title}',
                'time': meeting.created_at,
                'icon': 'calendar',
                'color': 'warning',
            })
        
        # Sort by time and limit
        recent_activities.sort(key=lambda x: x['time'], reverse=True)
        return recent_activities[:limit]
    
    @staticmethod
    def get_user_dashboard_data(user):
        """Get comprehensive dashboard data for a user"""
        return {
            'member_stats': DashboardService.get_member_stats(),
            'payment_stats': DashboardService.get_payment_stats(),
            'meeting_stats': DashboardService.get_meeting_stats(),
            'compliance_stats': DashboardService.get_compliance_stats(),
            'recent_activity': DashboardService.get_recent_activity(),
            'user': {
                'name': user.get_full_name(),
                'username': user.username,
                'roles': [ur.role.name for ur in user.userrole_set.filter(is_active=True)],
            },
            'date': timezone.now(),
        }
