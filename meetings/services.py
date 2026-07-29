from django.utils import timezone
from django.db.models import Count, Q
from .models import Meeting, Attendance
from members.models import Member

class MeetingService:
    """Service layer for meeting operations"""
    
    @staticmethod
    def get_upcoming_meetings(limit=5):
        """Get upcoming meetings"""
        return Meeting.objects.filter(
            date__gte=timezone.now(),
            status='scheduled'
        ).order_by('date')[:limit]
    
    @staticmethod
    def get_meeting_stats():
        """Get meeting statistics"""
        total = Meeting.objects.count()
        upcoming = Meeting.objects.filter(
            date__gte=timezone.now(),
            status='scheduled'
        ).count()
        today = Meeting.objects.filter(
            date__date=timezone.now().date(),
            status__in=['scheduled', 'ongoing']
        ).count()
        completed = Meeting.objects.filter(status='completed').count()
        
        return {
            'total': total,
            'upcoming': upcoming,
            'today': today,
            'completed': completed,
        }
    
    @staticmethod
    def get_attendance_stats(meeting):
        """Get attendance statistics for a meeting"""
        attendees = Attendance.objects.filter(meeting=meeting)
        total_members = Member.objects.filter(status='active').count()
        
        return {
            'total_members': total_members,
            'present': attendees.filter(status='present').count(),
            'absent': attendees.filter(status='absent').count(),
            'excused': attendees.filter(status='excused').count(),
            'late': attendees.filter(status='late').count(),
            'attendance_rate': attendees.filter(status='present').count() / total_members * 100 if total_members > 0 else 0,
        }
    
    @staticmethod
    def get_member_attendance(member, months=6):
        """Get attendance history for a member"""
        from datetime import datetime, timedelta
        
        start_date = timezone.now() - timedelta(days=30*months)
        attendances = Attendance.objects.filter(
            member=member,
            meeting__date__gte=start_date
        ).select_related('meeting')
        
        total = attendances.count()
        present = attendances.filter(status='present').count()
        
        return {
            'total': total,
            'present': present,
            'absent': total - present - attendances.filter(status='excused').count(),
            'excused': attendances.filter(status='excused').count(),
            'attendance_rate': present / total * 100 if total > 0 else 0,
        }
    
    @staticmethod
    def auto_mark_attendance(meeting):
        """Auto-mark attendance for members who checked in via QR"""
        # This would integrate with QR code check-in system
        pass
    
    @staticmethod
    def send_meeting_reminders(meeting):
        """Send reminders for a meeting"""
        from communications.models import Notification
        
        members = Member.objects.filter(status='active')
        for member in members:
            Notification.objects.create(
                recipient=member.user,
                notification_type='meeting_reminder',
                title=f'Reminder: {meeting.title}',
                message=f'Meeting tomorrow at {meeting.venue}. Time: {meeting.date.strftime("%H:%M")}',
                action_url=f'/meetings/{meeting.id}/'
            )
