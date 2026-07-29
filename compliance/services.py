from django.utils import timezone
from django.db.models import Count, Q, Sum
from datetime import timedelta
from .models import ComplianceRule, ComplianceScore, ComplianceAlert
from members.models import Member
from finance.models import Payment
from meetings.models import Attendance, Meeting

class ComplianceService:
    """Service layer for compliance operations"""
    
    @staticmethod
    def calculate_member_score(member):
        """Calculate compliance score for a single member"""
        # Calculate payment compliance
        payment_score = ComplianceService._calculate_payment_score(member)
        
        # Calculate attendance compliance
        attendance_score = ComplianceService._calculate_attendance_score(member)
        
        # Overall score (average)
        overall_score = (payment_score + attendance_score) / 2
        
        return {
            'score': overall_score,
            'payment_score': payment_score,
            'attendance_score': attendance_score,
        }
    
    @staticmethod
    def _calculate_payment_score(member):
        """Calculate payment compliance score"""
        from finance.models import Payment
        
        # Get completed payments
        payments = Payment.objects.filter(
            member=member,
            status='completed'
        )
        
        if not payments.exists():
            return 50  # Default score for no payments
        
        # Calculate based on categories
        categories = Payment.objects.filter(
            member=member,
            status='completed'
        ).values_list('category', flat=True).distinct()
        
        total_categories = Payment.objects.filter(
            member=member
        ).values_list('category', flat=True).distinct().count()
        
        if total_categories == 0:
            return 100
        
        score = (categories.count() / total_categories) * 100
        return min(100, score)
    
    @staticmethod
    def _calculate_attendance_score(member):
        """Calculate attendance compliance score"""
        # Get meetings in last 3 months
        three_months_ago = timezone.now() - timedelta(days=90)
        meetings = Meeting.objects.filter(
            date__gte=three_months_ago,
            status='completed'
        )
        
        if meetings.count() == 0:
            return 100
        
        attended = Attendance.objects.filter(
            member=member,
            meeting__in=meetings,
            status='present'
        ).count()
        
        score = (attended / meetings.count()) * 100
        return min(100, score)
    
    @staticmethod
    def check_member(member):
        """Run compliance check for a single member"""
        # Get or create compliance score
        score, created = ComplianceScore.objects.get_or_create(
            member=member,
            defaults={
                'score': 100,
                'payment_compliance': 100,
                'attendance_compliance': 100,
                'status': 'green'
            }
        )
        
        # Calculate scores
        scores = ComplianceService.calculate_member_score(member)
        
        # Update scores
        score.score = scores['score']
        score.payment_compliance = scores['payment_score']
        score.attendance_compliance = scores['attendance_score']
        score.update_status()
        score.save()
        
        return {
            'score': score,
            'updated': True
        }
    
    @staticmethod
    def check_all_members():
        """Run compliance check for all members"""
        members = Member.objects.filter(status='active')
        updated = 0
        
        for member in members:
            try:
                ComplianceService.check_member(member)
                updated += 1
            except Exception as e:
                print(f"Error checking member {member.member_id}: {str(e)}")
        
        return {
            'total': members.count(),
            'updated': updated
        }
    
    @staticmethod
    def get_member_history(member, days=30):
        """Get compliance history for a member"""
        history = []
        try:
            score = ComplianceScore.objects.get(member=member)
            history.append({
                'date': score.last_checked,
                'score': float(score.score),
                'status': score.status,
            })
        except ComplianceScore.DoesNotExist:
            pass
        return history
    
    @staticmethod
    def get_summary_stats():
        """Get summary statistics"""
        total_members = Member.objects.filter(status='active').count()
        green = ComplianceScore.objects.filter(status='green').count()
        yellow = ComplianceScore.objects.filter(status='yellow').count()
        red = ComplianceScore.objects.filter(status='red').count()
        
        return {
            'total_members': total_members,
            'green': green,
            'yellow': yellow,
            'red': red,
            'compliance_rate': (green / total_members * 100) if total_members > 0 else 0,
        }
    
    @staticmethod
    def get_alerts_summary():
        """Get alerts summary"""
        active_alerts = ComplianceAlert.objects.filter(is_resolved=False)
        
        return {
            'total': active_alerts.count(),
            'high': active_alerts.filter(priority='high').count(),
            'medium': active_alerts.filter(priority='medium').count(),
            'low': active_alerts.filter(priority='low').count(),
            'urgent': active_alerts.filter(priority='urgent').count(),
        }
