from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.http import HttpResponse
from django.utils import timezone
from django.db.models import Sum
import csv
import json

class ReportViewSet(viewsets.ViewSet):
    """API endpoint for reports"""
    permission_classes = [permissions.IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def members(self, request):
        """Generate members report"""
        from members.models import Member
        members = Member.objects.all()
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="members_report_{timezone.now().strftime("%Y%m%d")}.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['Member ID', 'Name', 'Phone', 'Status', 'Compliance', 'Joined'])
        
        for member in members:
            writer.writerow([
                member.member_id,
                member.get_full_name(),
                member.user.phone,
                member.status,
                member.compliance_status,
                member.date_joined.strftime('%Y-%m-%d')
            ])
        
        return response
    
    @action(detail=False, methods=['get'])
    def payments(self, request):
        """Generate payments report"""
        from finance.models import Payment
        payments = Payment.objects.filter(status='completed')
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="payments_report_{timezone.now().strftime("%Y%m%d")}.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['Member', 'Category', 'Amount', 'Method', 'Date'])
        
        for payment in payments:
            writer.writerow([
                payment.member.get_full_name(),
                payment.category.name,
                payment.amount,
                payment.get_payment_method_display(),
                payment.created_at.strftime('%Y-%m-%d')
            ])
        
        return response
    
    @action(detail=False, methods=['get'])
    def compliance(self, request):
        """Generate compliance report"""
        from compliance.models import ComplianceScore
        scores = ComplianceScore.objects.all()
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="compliance_report_{timezone.now().strftime("%Y%m%d")}.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['Member', 'Status', 'Score', 'Payment Score', 'Attendance Score'])
        
        for score in scores:
            writer.writerow([
                score.member.get_full_name(),
                score.status,
                score.score,
                score.payment_compliance,
                score.attendance_compliance
            ])
        
        return response
    
    @action(detail=False, methods=['get'])
    def summary(self, request):
        """Get summary report as JSON"""
        from members.models import Member
        from finance.models import Payment
        from meetings.models import Meeting
        from compliance.models import ComplianceScore
        from django.db.models import Sum
        
        data = {
            'generated_at': timezone.now().isoformat(),
            'members': {
                'total': Member.objects.count(),
                'active': Member.objects.filter(status='active').count(),
                'pending': Member.objects.filter(status='pending').count(),
            },
            'payments': {
                'total': Payment.objects.filter(status='completed').count(),
                'amount': Payment.objects.filter(status='completed').aggregate(
                    total=Sum('amount')
                )['total'] or 0,
            },
            'meetings': {
                'total': Meeting.objects.count(),
                'scheduled': Meeting.objects.filter(status='scheduled').count(),
                'completed': Meeting.objects.filter(status='completed').count(),
            },
            'compliance': {
                'green': ComplianceScore.objects.filter(status='green').count(),
                'yellow': ComplianceScore.objects.filter(status='yellow').count(),
                'red': ComplianceScore.objects.filter(status='red').count(),
            }
        }
        
        return Response(data)
