from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q
from members.models import Member, MemberNote
from .serializers import MemberSerializer, MemberCreateSerializer, MemberNoteSerializer

class MemberViewSet(viewsets.ModelViewSet):
    """API endpoint for members"""
    queryset = Member.objects.all()
    serializer_class = MemberSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return MemberCreateSerializer
        return MemberSerializer
    
    def get_queryset(self):
        """Filter members"""
        queryset = Member.objects.all()
        
        # Search
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(user__first_name__icontains=search) |
                Q(user__last_name__icontains=search) |
                Q(user__phone__icontains=search) |
                Q(member_id__icontains=search)
            )
        
        # Filter by status
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        return queryset
    
    @action(detail=True, methods=['get'])
    def notes(self, request, pk=None):
        """Get notes for a member"""
        member = self.get_object()
        notes = member.member_notes_list.all().order_by('-created_at')
        serializer = MemberNoteSerializer(notes, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def add_note(self, request, pk=None):
        """Add a note to a member"""
        member = self.get_object()
        content = request.data.get('content')
        is_private = request.data.get('is_private', False)
        
        if not content:
            return Response({
                'status': 'error',
                'message': 'Content is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        note = MemberNote.objects.create(
            member=member,
            author=request.user,
            content=content,
            is_private=is_private
        )
        
        serializer = MemberNoteSerializer(note)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['get'])
    def compliance(self, request, pk=None):
        """Get compliance status for a member"""
        member = self.get_object()
        from compliance.models import ComplianceScore
        
        try:
            score = ComplianceScore.objects.get(member=member)
            data = {
                'status': score.status,
                'score': score.score,
                'payment_compliance': score.payment_compliance,
                'attendance_compliance': score.attendance_compliance,
                'warnings': score.warnings,
                'last_checked': score.last_checked
            }
        except ComplianceScore.DoesNotExist:
            data = {
                'status': 'unknown',
                'score': 0,
                'payment_compliance': 0,
                'attendance_compliance': 0,
                'warnings': [],
                'last_checked': None
            }
        
        return Response(data)
    
    @action(detail=True, methods=['get'])
    def payments(self, request, pk=None):
        """Get payments for a member"""
        member = self.get_object()
        from finance.models import Payment
        from api.v1.finance.serializers import PaymentSerializer
        
        payments = Payment.objects.filter(
            member=member,
            status='completed'
        ).order_by('-created_at')
        
        serializer = PaymentSerializer(payments, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def attendance(self, request, pk=None):
        """Get attendance for a member"""
        member = self.get_object()
        from meetings.models import Attendance
        from api.v1.meetings.serializers import AttendanceSerializer
        
        attendances = Attendance.objects.filter(
            member=member
        ).order_by('-meeting__date')
        
        serializer = AttendanceSerializer(attendances, many=True)
        return Response(serializer.data)
