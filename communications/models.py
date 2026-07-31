from django.db import models
from django.conf import settings
from django.utils import timezone
from core.models import BaseModel
import jwt
import random
import string
from datetime import datetime, timedelta
import hashlib
import time


class Notification(BaseModel):
    """Notification model for system alerts"""
    NOTIFICATION_TYPES = (
        ('payment_reminder', 'Payment Reminder'),
        ('payment_received', 'Payment Received'),
        ('payment_approved', 'Payment Approved'),
        ('attendance_alert', 'Attendance Alert'),
        ('meeting_reminder', 'Meeting Reminder'),
        ('meeting_scheduled', 'Meeting Scheduled'),
        ('meeting_cancelled', 'Meeting Cancelled'),
        ('welfare_alert', 'Welfare Alert'),
        ('welfare_event', 'Welfare Event'),
        ('welfare_target', 'Welfare Target Reached'),
        ('compliance_alert', 'Compliance Alert'),
        ('compliance_update', 'Compliance Update'),
        ('system', 'System Notification'),
        ('announcement', 'Announcement'),
        ('member_registered', 'Member Registered'),
        ('report_ready', 'Report Ready'),
        ('chat_message', 'Chat Message'),
    )
    
    CHANNEL_CHOICES = (
        ('push', 'Push Notification'),
        ('sms', 'SMS'),
        ('email', 'Email'),
        ('in_app', 'In-App'),
    )
    
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('sent', 'Sent'),
        ('delivered', 'Delivered'),
        ('read', 'Read'),
        ('failed', 'Failed'),
    )
    
    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications',
        null=True,
        blank=True
    )
    notification_type = models.CharField(max_length=50, choices=NOTIFICATION_TYPES)
    title = models.CharField(max_length=200)
    message = models.TextField()
    channel = models.CharField(max_length=20, choices=CHANNEL_CHOICES, default='in_app')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    action_url = models.URLField(blank=True, null=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    read_at = models.DateTimeField(null=True, blank=True)
    is_announcement = models.BooleanField(default=False)
    priority = models.CharField(max_length=10, default='normal', choices=(
        ('low', 'Low'),
        ('normal', 'Normal'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ))
    related_id = models.IntegerField(null=True, blank=True)
    related_model = models.CharField(max_length=50, blank=True, null=True)
    
    class Meta:
        db_table = 'notifications'
        ordering = ['-created_at']
        verbose_name = 'Notification'
        verbose_name_plural = 'Notifications'
    
    def __str__(self):
        if self.recipient:
            return f"{self.title} - {self.recipient.get_full_name()}"
        return f"{self.title} - No recipient"
    
    def mark_as_read(self):
        self.status = 'read'
        self.read_at = timezone.now()
        self.save()
    
    def mark_as_sent(self):
        self.status = 'sent'
        self.sent_at = timezone.now()
        self.save()
    
    @classmethod
    def create_notification(cls, recipient, notification_type, title, message, 
                           action_url=None, priority='normal', related_id=None, 
                           related_model=None, channel='in_app'):
        notification = cls.objects.create(
            recipient=recipient,
            notification_type=notification_type,
            title=title,
            message=message,
            channel=channel,
            priority=priority,
            action_url=action_url,
            related_id=related_id,
            related_model=related_model,
            status='pending'
        )
        if channel == 'in_app':
            notification.mark_as_sent()
        return notification
    
    @classmethod
    def create_bulk_notifications(cls, recipients, notification_type, title, message,
                                  action_url=None, priority='normal', related_id=None,
                                  related_model=None, channel='in_app'):
        notifications = []
        for recipient in recipients:
            notifications.append(
                cls(
                    recipient=recipient,
                    notification_type=notification_type,
                    title=title,
                    message=message,
                    channel=channel,
                    priority=priority,
                    action_url=action_url,
                    related_id=related_id,
                    related_model=related_model,
                    status='pending'
                )
            )
        return cls.objects.bulk_create(notifications)


class Announcement(BaseModel):
    """Group announcements"""
    title = models.CharField(max_length=200)
    content = models.TextField()
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='announcements'
    )
    is_published = models.BooleanField(default=False)
    published_at = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    target_roles = models.JSONField(default=list, blank=True)
    is_global = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'announcements'
        ordering = ['-created_at']
        verbose_name = 'Announcement'
        verbose_name_plural = 'Announcements'
    
    def __str__(self):
        return self.title


class ChatRoom(BaseModel):
    """Chat room for conversations"""
    ROOM_TYPES = (
        ('direct', 'Direct Message'),
        ('group', 'Group Chat'),
        ('committee', 'Committee Chat'),
        ('meeting', 'Meeting Chat'),
    )
    
    name = models.CharField(max_length=100, blank=True)
    room_type = models.CharField(max_length=20, choices=ROOM_TYPES, default='group')
    members = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='chat_rooms',
        blank=True
    )
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_rooms'
    )
    last_message = models.ForeignKey(
        'ChatMessage',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='last_message_room'
    )
    last_message_time = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'chat_rooms'
        ordering = ['-last_message_time', '-created_at']
        verbose_name = 'Chat Room'
        verbose_name_plural = 'Chat Rooms'
    
    def __str__(self):
        return self.name or f"Room {self.id}"
    
    def get_unread_count(self, user):
        return ChatMessage.objects.filter(
            room=self,
            is_deleted=False
        ).exclude(sender=user).count()


class ChatMessage(BaseModel):
    """Chat messages"""
    MESSAGE_TYPES = (
        ('text', 'Text'),
        ('image', 'Image'),
        ('file', 'File'),
        ('announcement', 'Announcement'),
        ('system', 'System'),
    )
    
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='chat_messages'
    )
    message_type = models.CharField(max_length=20, choices=MESSAGE_TYPES, default='text')
    content = models.TextField()
    file_attachment = models.FileField(upload_to='chat_files/', null=True, blank=True)
    is_announcement = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)
    read_by = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='read_messages',
        blank=True
    )
    
    class Meta:
        db_table = 'chat_messages'
        ordering = ['created_at']
        verbose_name = 'Chat Message'
        verbose_name_plural = 'Chat Messages'
    
    def __str__(self):
        return f"{self.sender.username}: {self.content[:50]}"
    
    def soft_delete(self):
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.save()


class MeetingRoom(BaseModel):
    """Video meeting rooms for chat"""
    ROOM_STATUS = (
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('ended', 'Ended'),
    )
    
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    chat_room = models.ForeignKey(
        ChatRoom,
        on_delete=models.CASCADE,
        related_name='meeting_rooms',
        null=True,
        blank=True
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='created_meeting_rooms'
    )
    room_code = models.CharField(max_length=50, unique=True, blank=True)
    status = models.CharField(max_length=20, choices=ROOM_STATUS, default='active')
    scheduled_start = models.DateTimeField(null=True, blank=True)
    scheduled_end = models.DateTimeField(null=True, blank=True)
    attendees = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='meeting_rooms',
        blank=True
    )
    meeting_url = models.URLField(blank=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'meeting_rooms'
        ordering = ['-created_at']
        verbose_name = 'Meeting Room'
        verbose_name_plural = 'Meeting Rooms'
    
    def __str__(self):
        return f"{self.name} - {self.room_code}"
    
    def save(self, *args, **kwargs):
        if not self.room_code:
            timestamp = str(int(time.time()))[-8:]
            random_part = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
            name_slug = self.name.lower().replace(' ', '-')[:15]
            name_slug = ''.join(c if c.isalnum() or c == '-' else '-' for c in name_slug)
            self.room_code = f"{name_slug}-{timestamp}-{random_part}"[:50]
        if not self.meeting_url:
            self.meeting_url = f"https://meet.jit.si/{self.room_code}"
        super().save(*args, **kwargs)
    
    def get_meeting_link(self, user=None):
        meeting_id = self.room_code
        base_url = f"https://meet.jit.si/{meeting_id}"
        params = []
        if user:
            params.append(f"userName={user.get_full_name()}")
        params.append("config.prejoinPageEnabled=false")
        params.append("config.enableWelcomePage=false")
        params.append("interfaceConfig.APP_NAME=LakChogo Connect")
        is_host = user and user.id == self.created_by.id
        if is_host:
            params.append("config.startWithAudioMuted=false")
            params.append("config.startWithVideoMuted=false")
        return f"{base_url}?{'&'.join(params)}" if params else base_url
