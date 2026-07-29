from django.db import models
from django.conf import settings
from core.models import BaseModel
from members.models import Member

class Meeting(BaseModel):
    title = models.CharField(max_length=200)
    date = models.DateTimeField()
    venue = models.CharField(max_length=200)
    agenda = models.TextField(blank=True)
    minutes_text = models.TextField(blank=True)
    minutes_url = models.URLField(blank=True)
    status = models.CharField(max_length=20, choices=(
        ('scheduled', 'Scheduled'),
        ('ongoing', 'Ongoing'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ), default='scheduled')
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    
    class Meta:
        db_table = 'meetings'
        ordering = ['-date']
        verbose_name = 'Meeting'
        verbose_name_plural = 'Meetings'
    
    def __str__(self):
        return self.title


class Attendance(BaseModel):
    ATTENDANCE_STATUS = (
        ('present', 'Present'),
        ('absent', 'Absent'),
        ('excused', 'Excused'),
    )
    
    meeting = models.ForeignKey(Meeting, on_delete=models.CASCADE, related_name='attendances')
    member = models.ForeignKey(Member, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=ATTENDANCE_STATUS, default='absent')
    check_in_method = models.CharField(max_length=20, choices=(
        ('qr', 'QR Code'),
        ('manual', 'Manual'),
    ), blank=True)
    check_in_time = models.DateTimeField(null=True, blank=True)
    gps_coordinates = models.CharField(max_length=100, blank=True)
    notes = models.TextField(blank=True)
    
    class Meta:
        db_table = 'attendances'
        unique_together = ['meeting', 'member']
        verbose_name = 'Attendance'
        verbose_name_plural = 'Attendances'
    
    def __str__(self):
        return f"{self.member.get_full_name()} - {self.meeting.title} - {self.status}"
