from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from meetings.models import Meeting, Attendance
from .serializers import MeetingSerializer, AttendanceSerializer

class MeetingViewSet(viewsets.ModelViewSet):
    """API endpoint for meetings"""
    queryset = Meeting.objects.all().order_by('-date')
    serializer_class = MeetingSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Filter meetings"""
        queryset = Meeting.objects.all().order_by('-date')
        
        # Filter by status
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        # Upcoming meetings
        upcoming = self.request.query_params.get('upcoming')
        if upcoming == 'true':
            queryset = queryset.filter(
                date__gte=timezone.now(),
                status='scheduled'
            )
        
        return queryset
    
    @action(detail=True, methods=['post'])
    def check_in(self, request, pk=None):
        """Check in to a meeting via QR code"""
        meeting = self.get_object()
        member_id = request.data.get('member_id')
        
        if not member_id:
            return Response({
                'status': 'error',
                'message': 'Member ID required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        from members.models import Member
        try:
            member = Member.objects.get(member_id=member_id)
        except Member.DoesNotExist:
            return Response({
                'status': 'error',
                'message': 'Member not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        attendance, created = Attendance.objects.get_or_create(
            meeting=meeting,
            member=member,
            defaults={
                'status': 'present',
                'check_in_method': 'qr',
                'check_in_time': timezone.now(),
                'recorded_by': request.user
            }
        )
        
        if not created:
            attendance.status = 'present'
            attendance.check_in_time = timezone.now()
            attendance.save()
        
        return Response({
            'status': 'success',
            'attendance': AttendanceSerializer(attendance).data
        })
    
    @action(detail=True, methods=['get'])
    def attendance(self, request, pk=None):
        """Get attendance for a meeting"""
        meeting = self.get_object()
        attendances = Attendance.objects.filter(meeting=meeting)
        serializer = AttendanceSerializer(attendances, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def stats(self, request, pk=None):
        """Get meeting statistics"""
        meeting = self.get_object()
        attendances = Attendance.objects.filter(meeting=meeting)
        
        return Response({
            'total': attendances.count(),
            'present': attendances.filter(status='present').count(),
            'absent': attendances.filter(status='absent').count(),
            'excused': attendances.filter(status='excused').count(),
            'late': attendances.filter(status='late').count()
        })
