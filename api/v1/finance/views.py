from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Sum
from finance.models import Payment, PaymentCategory
from .serializers import PaymentSerializer, CategorySerializer

class PaymentViewSet(viewsets.ModelViewSet):
    """API endpoint for payments"""
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Filter payments"""
        queryset = Payment.objects.all().order_by('-created_at')
        
        # Filter by member
        member_id = self.request.query_params.get('member')
        if member_id:
            queryset = queryset.filter(member__member_id=member_id)
        
        # Filter by category
        category_id = self.request.query_params.get('category')
        if category_id:
            queryset = queryset.filter(category__id=category_id)
        
        # Filter by status
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        return queryset
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get payment statistics"""
        total = Payment.objects.filter(status='completed').aggregate(
            total=Sum('amount')
        )['total'] or 0
        
        pending = Payment.objects.filter(status='pending').count()
        
        return Response({
            'total': total,
            'pending': pending,
            'count': Payment.objects.filter(status='completed').count()
        })
    
    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """Approve a pending payment"""
        payment = self.get_object()
        
        if payment.status != 'pending':
            return Response({
                'status': 'error',
                'message': 'Payment is not pending'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        payment.verify(request.user)
        
        return Response({
            'status': 'success',
            'message': 'Payment approved successfully'
        })
    
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Cancel a payment"""
        payment = self.get_object()
        
        if payment.status in ['completed', 'refunded']:
            return Response({
                'status': 'error',
                'message': 'Cannot cancel completed or refunded payment'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        payment.cancel()
        
        return Response({
            'status': 'success',
            'message': 'Payment cancelled successfully'
        })


class CategoryViewSet(viewsets.ModelViewSet):
    """API endpoint for payment categories"""
    queryset = PaymentCategory.objects.filter(is_active=True)
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get category statistics"""
        categories = PaymentCategory.objects.filter(is_active=True)
        stats = []
        
        for category in categories:
            total = Payment.objects.filter(
                category=category,
                status='completed'
            ).aggregate(total=Sum('amount'))['total'] or 0
            
            count = Payment.objects.filter(
                category=category,
                status='completed'
            ).count()
            
            stats.append({
                'id': category.id,
                'name': category.name,
                'total': total,
                'count': count
            })
        
        return Response(stats)
