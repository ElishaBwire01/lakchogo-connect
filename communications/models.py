from django.db import models
from django.conf import settings
from django.utils import timezone
from core.models import BaseModel

class Notification(BaseModel):
    NOTIFICATION_TYPES = (
        ('payment_reminder', 'Payment Reminder'),
        ('attendance_alert', 'Attendance Alert'),
        ('meeting_reminder', 'Meeting Reminder'),
        ('welfare_alert', 'Welfare Alert'),
        ('compliance_alert', 'Compliance Alert'),
        ('system', 'System Notification'),
        ('announcement', 'Announcement'),
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
        related_name='notifications'
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
    
    class Meta:
        db_table = 'notifications'
        ordering = ['-created_at']
        verbose_name = 'Notification'
        verbose_name_plural = 'Notifications'
    
    def __str__(self):
        return f"{self.title} - {self.recipient.get_full_name()}"
    
    def mark_as_read(self):
        self.status = 'read'
        self.read_at = timezone.now()
        self.save()
    
    def mark_as_sent(self):
        self.status = 'sent'
        self.sent_at = timezone.now()
        self.save()


class Announcement(BaseModel):
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
    
    def publish(self):
        self.is_published = True
        self.published_at = timezone.now()
        self.save()


class ChatRoom(BaseModel):
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
    
    class Meta:
        db_table = 'chat_rooms'
        ordering = ['-created_at']
        verbose_name = 'Chat Room'
        verbose_name_plural = 'Chat Rooms'
    
    def __str__(self):
        return self.name or f"Room {self.id}"


class ChatMessage(BaseModel):
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
