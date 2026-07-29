from django.db import models
from django.conf import settings
from django.utils import timezone
from core.models import BaseModel
from members.models import Member

class Meeting(BaseModel):
    """Meeting model for scheduling and managing meetings"""
    STATUS_CHOICES = (
        ('scheduled', 'Scheduled'),
        ('ongoing', 'Ongoing'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    )
    
    title = models.CharField(max_length=200, help_text="Meeting title/agenda topic")
    description = models.TextField(blank=True, help_text="Detailed description of the meeting")
    date = models.DateTimeField(help_text="Date and time of the meeting")
    venue = models.CharField(max_length=200, help_text="Physical or virtual meeting location")
    agenda = models.TextField(blank=True, help_text="Meeting agenda items")
    minutes_text = models.TextField(blank=True, help_text="Meeting minutes in text format")
    minutes_url = models.URLField(blank=True, help_text="URL to uploaded minutes document")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled')
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='created_meetings',
        help_text="User who created this meeting"
    )
    qr_code = models.CharField(max_length=255, blank=True, help_text="QR code for attendance")
    
    class Meta:
        db_table = 'meetings'
        ordering = ['-date']
        verbose_name = 'Meeting'
        verbose_name_plural = 'Meetings'
    
    def __str__(self):
        return f"{self.title} - {self.date.strftime('%Y-%m-%d %H:%M')}"
    
    def is_upcoming(self):
        return self.date > timezone.now() and self.status == 'scheduled'
    
    def is_past(self):
        return self.date < timezone.now()
    
    def get_attendance_count(self):
        return self.attendances.filter(status='present').count()
    
    def get_absent_count(self):
        return self.attendances.filter(status='absent').count()


class Attendance(BaseModel):
    """Attendance tracking for meetings"""
    ATTENDANCE_STATUS = (
        ('present', 'Present'),
        ('absent', 'Absent'),
        ('excused', 'Excused'),
        ('late', 'Late'),
    )
    
    CHECK_IN_METHODS = (
        ('qr', 'QR Code'),
        ('manual', 'Manual'),
        ('gps', 'GPS'),
        ('fingerprint', 'Fingerprint'),
    )
    
    meeting = models.ForeignKey(
        Meeting,
        on_delete=models.CASCADE,
        related_name='attendances',
        help_text="Meeting this attendance belongs to"
    )
    member = models.ForeignKey(
        Member,
        on_delete=models.CASCADE,
        related_name='attendances',
        help_text="Member whose attendance is being recorded"
    )
    status = models.CharField(
        max_length=20,
        choices=ATTENDANCE_STATUS,
        default='absent',
        help_text="Attendance status"
    )
    check_in_method = models.CharField(
        max_length=20,
        choices=CHECK_IN_METHODS,
        blank=True,
        help_text="How the member checked in"
    )
    check_in_time = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Time the member checked in"
    )
    check_out_time = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Time the member checked out"
    )
    gps_coordinates = models.CharField(
        max_length=100,
        blank=True,
        help_text="GPS coordinates of check-in"
    )
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        help_text="IP address of check-in device"
    )
    device_info = models.CharField(
        max_length=255,
        blank=True,
        help_text="Device information"
    )
    notes = models.TextField(blank=True, help_text="Additional notes")
    recorded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='recorded_attendances',
        help_text="User who recorded this attendance"
    )
    
    class Meta:
        db_table = 'attendances'
        unique_together = ['meeting', 'member']
        ordering = ['-created_at']
        verbose_name = 'Attendance'
        verbose_name_plural = 'Attendances'
    
    def __str__(self):
        return f"{self.member.get_full_name()} - {self.meeting.title} - {self.status}"
    
    def mark_present(self):
        self.status = 'present'
        self.check_in_time = timezone.now()
        self.save()
    
    def mark_absent(self):
        self.status = 'absent'
        self.save()
    
    def mark_excused(self):
        self.status = 'excused'
        self.save()


class MeetingMinutes(BaseModel):
    """Meeting minutes/notes"""
    meeting = models.OneToOneField(
        Meeting,
        on_delete=models.CASCADE,
        related_name='minutes',
        help_text="Meeting these minutes belong to"
    )
    content = models.TextField(help_text="Full minutes content")
    summary = models.TextField(blank=True, help_text="Brief summary of the meeting")
    decisions = models.JSONField(default=list, blank=True, help_text="List of decisions made")
    action_items = models.JSONField(default=list, blank=True, help_text="List of action items")
    attendees_count = models.IntegerField(default=0, help_text="Number of attendees")
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_minutes',
        help_text="User who approved these minutes"
    )
    approved_at = models.DateTimeField(null=True, blank=True)
    file_attachment = models.FileField(
        upload_to='minutes/',
        null=True,
        blank=True,
        help_text="Uploaded minutes file"
    )
    
    class Meta:
        db_table = 'meeting_minutes'
        ordering = ['-created_at']
        verbose_name = 'Meeting Minutes'
        verbose_name_plural = 'Meeting Minutes'
    
    def __str__(self):
        return f"Minutes: {self.meeting.title} - {self.created_at.strftime('%Y-%m-%d')}"
    
    def approve(self, user):
        self.approved_by = user
        self.approved_at = timezone.now()
        self.save()
