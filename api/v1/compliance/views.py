from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Count
from compliance.models import ComplianceScore, ComplianceAlert, ComplianceRule
from .serializers import ComplianceScoreSerializer, ComplianceAlertSerializer, ComplianceRuleSerializer

class ComplianceViewSet(viewsets.ModelViewSet):
    """API endpoint for compliance"""
    queryset = ComplianceScore.objects.all()
    serializer_class = ComplianceScoreSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Filter compliance scores"""
        queryset = ComplianceScore.objects.all()
        
        # Filter by status
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        # Filter by member
        member_id = self.request.query_params.get('member')
        if member_id:
            queryset = queryset.filter(member__member_id=member_id)
        
        return queryset
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get compliance statistics"""
        total = ComplianceScore.objects.count()
        green = ComplianceScore.objects.filter(status='green').count()
        yellow = ComplianceScore.objects.filter(status='yellow').count()
        red = ComplianceScore.objects.filter(status='red').count()
        
        return Response({
            'total': total,
            'green': green,
            'yellow': yellow,
            'red': red,
            'compliance_rate': (green / total * 100) if total > 0 else 0
        })
    
    @action(detail=False, methods=['get'])
    def alerts(self, request):
        """Get compliance alerts"""
        alerts = ComplianceAlert.objects.filter(is_resolved=False)
        
        # Filter by priority
        priority = request.query_params.get('priority')
        if priority:
            alerts = alerts.filter(priority=priority)
        
        serializer = ComplianceAlertSerializer(alerts, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def resolve_alert(self, request, pk=None):
        """Resolve a compliance alert"""
        alert = ComplianceAlert.objects.get(id=pk)
        alert.resolve(request.user, request.data.get('notes', ''))
        
        return Response({
            'status': 'success',
            'message': 'Alert resolved successfully'
        })
    
    @action(detail=False, methods=['post'])
    def run_check(self, request):
        """Run compliance check for all members"""
        from compliance.services import ComplianceService
        result = ComplianceService.check_all_members()
        
        return Response({
            'status': 'success',
            'message': f"Checked {result['updated']} members"
        })
    
    @action(detail=False, methods=['get'])
    def rules(self, request):
        """Get compliance rules"""
        rules = ComplianceRule.objects.filter(is_active=True)
        serializer = ComplianceRuleSerializer(rules, many=True)
        return Response(serializer.data)
