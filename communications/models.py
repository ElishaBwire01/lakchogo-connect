from django.db import models
from django.conf import settings
from django.utils import timezone
from core.models import BaseModel

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
    related_model = models.CharField(max_length=50, blank=True, null=True)  # Made nullable
    
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
    
    def mark_as_delivered(self):
        self.status = 'delivered'
        self.save()
    
    @classmethod
    def create_notification(cls, recipient, notification_type, title, message, 
                           action_url=None, priority='normal', related_id=None, 
                           related_model=None, channel='in_app'):
        """Create a notification"""
        notification = cls.objects.create(
            recipient=recipient,
            notification_type=notification_type,
            title=title,
            message=message,
            channel=channel,
            priority=priority,
            action_url=action_url,
            related_id=related_id,
            related_model=related_model,  # Can be None now
            status='pending'
        )
        if channel == 'in_app':
            notification.mark_as_sent()
        return notification
    
    @classmethod
    def create_bulk_notifications(cls, recipients, notification_type, title, message,
                                  action_url=None, priority='normal', related_id=None,
                                  related_model=None, channel='in_app'):
        """Create notifications for multiple recipients"""
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
                    related_model=related_model,  # Can be None now
                    status='pending'
                )
            )
        created = cls.objects.bulk_create(notifications)
        if channel == 'in_app':
            for notification in created:
                notification.mark_as_sent()
        return created


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
    
    def publish(self):
        self.is_published = True
        self.published_at = timezone.now()
        self.save()
        
        from django.contrib.auth import get_user_model
        User = get_user_model()
        users = User.objects.filter(is_active=True)
        
        notifications = []
        for user in users:
            notifications.append(
                Notification(
                    recipient=user,
                    notification_type='announcement',
                    title=f"📢 New Announcement: {self.title}",
                    message=self.content[:200],
                    action_url=f'/communications/announcements/{self.id}/',
                    status='sent',
                    sent_at=timezone.now()
                )
            )
        Notification.objects.bulk_create(notifications)


class ChatRoom(BaseModel):
    """Chat room for group conversations"""
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
        from .models import ChatMessage
        return ChatMessage.objects.filter(
            room=self,
            is_deleted=False
        ).exclude(
            sender=user
        ).count()


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
    
    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        
        if is_new and self.room:
            self.room.last_message = self
            self.room.last_message_time = self.created_at
            self.room.save()
            
            from .services import NotificationTriggers
            for member in self.room.members.exclude(id=self.sender.id):
                NotificationTriggers.chat_message_notification(
                    message=self,
                    recipient=member
                )
