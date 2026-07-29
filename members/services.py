from django.db.models import Count, Sum, Q
from django.utils import timezone
from datetime import timedelta
from .models import Member, MemberContributionSummary
from finance.models import Payment, PaymentCategory
from meetings.models import Attendance, Meeting

class MemberService:
    """Service layer for member operations"""
    
    @staticmethod
    def get_member_stats():
        """Get member statistics"""
        total = Member.objects.count()
        active = Member.objects.filter(status='active').count()
        pending = Member.objects.filter(status='pending').count()
        inactive = Member.objects.filter(status='inactive').count()
        suspended = Member.objects.filter(status='suspended').count()
        
        # New members this month
        month_start = timezone.now().replace(day=1)
        new_this_month = Member.objects.filter(
            date_joined__gte=month_start
        ).count()
        
        return {
            'total': total,
            'active': active,
            'pending': pending,
            'inactive': inactive,
            'suspended': suspended,
            'new_this_month': new_this_month,
        }
    
    @staticmethod
    def get_member_contribution_summary(member_id):
        """Get contribution summary for a member"""
        try:
            member = Member.objects.get(member_id=member_id)
            summary, created = MemberContributionSummary.objects.get_or_create(member=member)
            if created or timezone.now() - summary.updated_at > timedelta(hours=1):
                summary.update_summary()
            return summary
        except Member.DoesNotExist:
            return None
    
    @staticmethod
    def update_all_summaries():
        """Update contribution summaries for all members"""
        members = Member.objects.all()
        updated = 0
        
        for member in members:
            summary, created = MemberContributionSummary.objects.get_or_create(member=member)
            summary.update_summary()
            updated += 1
        
        return {'total': members.count(), 'updated': updated}
    
    @staticmethod
    def get_member_attendance(member_id, months=3):
        """Get attendance history for a member"""
        try:
            member = Member.objects.get(member_id=member_id)
            start_date = timezone.now() - timedelta(days=30*months)
            
            attendances = Attendance.objects.filter(
                member=member,
                meeting__date__gte=start_date
            ).select_related('meeting').order_by('-meeting__date')
            
            return {
                'member': member,
                'attendances': attendances,
                'total': attendances.count(),
                'present': attendances.filter(status='present').count(),
                'absent': attendances.filter(status='absent').count(),
                'excused': attendances.filter(status='excused').count(),
            }
        except Member.DoesNotExist:
            return None
    
    @staticmethod
    def get_member_payments(member_id):
        """Get payment history for a member"""
        try:
            member = Member.objects.get(member_id=member_id)
            payments = Payment.objects.filter(
                member=member,
                status='completed'
            ).select_related('category').order_by('-created_at')
            
            total = payments.aggregate(total=Sum('amount'))['total'] or 0
            
            return {
                'member': member,
                'payments': payments,
                'total': total,
                'count': payments.count(),
            }
        except Member.DoesNotExist:
            return None
    
    @staticmethod
    def get_compliance_summary():
        """Get compliance summary for all members"""
        from compliance.models import ComplianceScore
        
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
    def search_members(query):
        """Search for members by name, phone, or ID"""
        if not query:
            return Member.objects.none()
        
        return Member.objects.filter(
            Q(user__first_name__icontains=query) |
            Q(user__last_name__icontains=query) |
            Q(user__phone__icontains=query) |
            Q(member_id__icontains=query)
        )
    
    @staticmethod
    def get_members_by_status(status):
        """Get members by status"""
        return Member.objects.filter(status=status)
