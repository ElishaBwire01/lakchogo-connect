from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Sum
from welfare.models import BereavementEvent, BereavementContribution
from .serializers import BereavementEventSerializer, BereavementContributionSerializer

class WelfareViewSet(viewsets.ModelViewSet):
    """API endpoint for welfare"""
    queryset = BereavementEvent.objects.all()
    serializer_class = BereavementEventSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Filter welfare events"""
        queryset = BereavementEvent.objects.all().order_by('-created_at')
        
        # Filter by status
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        # Filter by member
        member_id = self.request.query_params.get('member')
        if member_id:
            queryset = queryset.filter(member__member_id=member_id)
        
        return queryset
    
    @action(detail=True, methods=['post'])
    def contribute(self, request, pk=None):
        """Contribute to a welfare event"""
        event = self.get_object()
        amount = request.data.get('amount')
        contributor_id = request.data.get('contributor_id')
        
        if not amount:
            return Response({
                'status': 'error',
                'message': 'Amount required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        from members.models import Member
        contributor = None
        if contributor_id:
            try:
                contributor = Member.objects.get(id=contributor_id)
            except Member.DoesNotExist:
                return Response({
                    'status': 'error',
                    'message': 'Contributor not found'
                }, status=status.HTTP_404_NOT_FOUND)
        
        contribution = BereavementContribution.objects.create(
            event=event,
            contributor=contributor,
            amount=amount,
            contributor_name=request.data.get('contributor_name', ''),
            contributor_phone=request.data.get('contributor_phone', ''),
            payment_method=request.data.get('payment_method', 'cash'),
            notes=request.data.get('notes', ''),
            recorded_by=request.user
        )
        
        # Update event amount collected
        event.amount_collected += float(amount)
        event.save()
        
        return Response({
            'status': 'success',
            'contribution': BereavementContributionSerializer(contribution).data,
            'progress': event.progress_percentage
        })
    
    @action(detail=True, methods=['get'])
    def contributions(self, request, pk=None):
        """Get contributions for a welfare event"""
        event = self.get_object()
        contributions = event.contributions.all().order_by('-created_at')
        serializer = BereavementContributionSerializer(contributions, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get welfare statistics"""
        total_events = BereavementEvent.objects.count()
        active_events = BereavementEvent.objects.filter(status='active').count()
        
        total_collected = BereavementEvent.objects.aggregate(
            total=Sum('amount_collected')
        )['total'] or 0
        
        total_target = BereavementEvent.objects.aggregate(
            total=Sum('collection_target')
        )['total'] or 0
        
        return Response({
            'total_events': total_events,
            'active_events': active_events,
            'total_collected': total_collected,
            'total_target': total_target,
            'completion_rate': (total_collected / total_target * 100) if total_target > 0 else 0
        })
