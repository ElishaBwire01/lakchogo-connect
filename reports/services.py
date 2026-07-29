"""
Report services for LakChogo Connect
"""

from django.db.models import Sum, Count
from django.utils import timezone
from datetime import datetime
import json
from .models import Report

class ReportService:
    """Service for report generation"""
    
    def __init__(self):
        self.report = None
    
    def generate_report(self, report_id):
        """Generate a report"""
        from .models import Report
        self.report = Report.objects.get(id=report_id)
        
        if self.report.report_type == 'member':
            return self._generate_member_report()
        elif self.report.report_type == 'payment':
            return self._generate_payment_report()
        elif self.report.report_type == 'attendance':
            return self._generate_attendance_report()
        elif self.report.report_type == 'compliance':
            return self._generate_compliance_report()
        elif self.report.report_type == 'welfare':
            return self._generate_welfare_report()
        else:
            return self._generate_summary_report()
    
    def _generate_member_report(self):
        """Generate member report with proper CSV structure"""
        from members.models import Member
        members = Member.objects.all()
        
        # Create headers and rows for CSV
        headers = ['Member ID', 'Name', 'Phone', 'Email', 'Status', 'Compliance', 'Joined']
        rows = []
        
        for member in members:
            rows.append([
                member.member_id,
                member.get_full_name(),
                member.user.phone,
                member.user.email or '',
                member.status,
                member.compliance_status,
                member.date_joined.strftime('%Y-%m-%d')
            ])
        
        data = {
            'headers': headers,
            'rows': rows,
            'total': len(rows),
            'summary': {
                'total_members': members.count(),
                'active': members.filter(status='active').count(),
                'pending': members.filter(status='pending').count(),
            }
        }
        
        self.report.data = data
        self.report.save()
        return data
    
    def _generate_payment_report(self):
        """Generate payment report with proper CSV structure"""
        from finance.models import Payment
        payments = Payment.objects.filter(status='completed')
        
        headers = ['Member', 'Category', 'Amount', 'Method', 'Date']
        rows = []
        
        for payment in payments:
            rows.append([
                payment.member.get_full_name(),
                payment.category.name,
                str(payment.amount),
                payment.get_payment_method_display(),
                payment.created_at.strftime('%Y-%m-%d %H:%M')
            ])
        
        total_amount = payments.aggregate(total=Sum('amount'))['total'] or 0
        
        data = {
            'headers': headers,
            'rows': rows,
            'total': len(rows),
            'total_amount': float(total_amount),
            'summary': {
                'total_payments': payments.count(),
                'total_amount': float(total_amount),
            }
        }
        
        self.report.data = data
        self.report.save()
        return data
    
    def _generate_attendance_report(self):
        """Generate attendance report with proper CSV structure"""
        from meetings.models import Meeting, Attendance
        meetings = Meeting.objects.filter(status='completed')
        
        headers = ['Meeting', 'Date', 'Member', 'Status', 'Check-in Method']
        rows = []
        
        for meeting in meetings[:20]:
            attendances = Attendance.objects.filter(meeting=meeting)
            for attendance in attendances:
                rows.append([
                    meeting.title,
                    meeting.date.strftime('%Y-%m-%d'),
                    attendance.member.get_full_name(),
                    attendance.status,
                    attendance.check_in_method or 'N/A'
                ])
        
        data = {
            'headers': headers,
            'rows': rows,
            'total': len(rows),
            'summary': {
                'total_meetings': meetings.count(),
                'total_attendances': len(rows),
            }
        }
        
        self.report.data = data
        self.report.save()
        return data
    
    def _generate_compliance_report(self):
        """Generate compliance report with proper CSV structure"""
        from compliance.models import ComplianceScore
        scores = ComplianceScore.objects.all()
        
        headers = ['Member', 'Status', 'Score', 'Payment Score', 'Attendance Score', 'Warnings']
        rows = []
        
        for score in scores:
            rows.append([
                score.member.get_full_name(),
                score.status,
                str(score.score),
                str(score.payment_compliance),
                str(score.attendance_compliance),
                str(len(score.warnings))
            ])
        
        data = {
            'headers': headers,
            'rows': rows,
            'total': len(rows),
            'summary': {
                'total': scores.count(),
                'green': scores.filter(status='green').count(),
                'yellow': scores.filter(status='yellow').count(),
                'red': scores.filter(status='red').count(),
            }
        }
        
        self.report.data = data
        self.report.save()
        return data
    
    def _generate_welfare_report(self):
        """Generate welfare report with proper CSV structure"""
        from welfare.models import BereavementEvent
        events = BereavementEvent.objects.all()
        
        headers = ['Event Code', 'Member', 'Deceased', 'Target', 'Collected', 'Progress', 'Status']
        rows = []
        
        for event in events:
            rows.append([
                event.event_code,
                event.member.get_full_name(),
                event.deceased_name,
                str(event.collection_target),
                str(event.amount_collected),
                f"{event.progress_percentage:.1f}%",
                event.status
            ])
        
        total_collected = events.aggregate(total=Sum('amount_collected'))['total'] or 0
        total_target = events.aggregate(total=Sum('collection_target'))['total'] or 0
        
        data = {
            'headers': headers,
            'rows': rows,
            'total': len(rows),
            'summary': {
                'total_events': events.count(),
                'total_collected': float(total_collected),
                'total_target': float(total_target),
            }
        }
        
        self.report.data = data
        self.report.save()
        return data
    
    def _generate_summary_report(self):
        """Generate summary report"""
        from members.models import Member
        from finance.models import Payment
        from meetings.models import Meeting
        from compliance.models import ComplianceScore
        from welfare.models import BereavementEvent
        
        data = {
            'headers': ['Metric', 'Value'],
            'rows': [
                ['Total Members', str(Member.objects.count())],
                ['Active Members', str(Member.objects.filter(status='active').count())],
                ['Total Payments', str(Payment.objects.filter(status='completed').count())],
                ['Total Amount', f"KES {Payment.objects.filter(status='completed').aggregate(total=Sum('amount'))['total'] or 0}"],
                ['Total Meetings', str(Meeting.objects.count())],
                ['Completed Meetings', str(Meeting.objects.filter(status='completed').count())],
                ['Compliance Green', str(ComplianceScore.objects.filter(status='green').count())],
                ['Compliance Yellow', str(ComplianceScore.objects.filter(status='yellow').count())],
                ['Compliance Red', str(ComplianceScore.objects.filter(status='red').count())],
                ['Welfare Events', str(BereavementEvent.objects.count())],
                ['Active Welfare', str(BereavementEvent.objects.filter(status='active').count())],
            ],
            'generated_at': timezone.now().isoformat()
        }
        
        self.report.data = data
        self.report.save()
        return data
