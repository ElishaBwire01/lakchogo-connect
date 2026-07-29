from django.utils import timezone
from django.conf import settings
from .models import Notification, Announcement

class NotificationService:
    """Service for creating and managing notifications"""
    
    @staticmethod
    def send_notification(user, notification_type, title, message, 
                         channel='in_app', action_url=None, priority='normal'):
        """Create a notification for a user"""
        return Notification.objects.create(
            recipient=user,
            notification_type=notification_type,
            title=title,
            message=message,
            channel=channel,
            action_url=action_url,
            priority=priority,
            status='pending'
        )
    
    @staticmethod
    def send_bulk_notification(users, notification_type, title, message,
                               channel='in_app', action_url=None, priority='normal'):
        """Create notifications for multiple users"""
        notifications = []
        for user in users:
            notifications.append(
                Notification(
                    recipient=user,
                    notification_type=notification_type,
                    title=title,
                    message=message,
                    channel=channel,
                    action_url=action_url,
                    priority=priority,
                    status='pending'
                )
            )
        return Notification.objects.bulk_create(notifications)
    
    @staticmethod
    def get_unread_count(user):
        """Get unread notification count for a user"""
        return Notification.objects.filter(
            recipient=user,
            status__in=['pending', 'sent']
        ).count()

class AnnouncementService:
    """Service for managing announcements"""
    
    @staticmethod
    def publish_announcement(title, content, author, is_global=True, 
                            target_roles=None, expires_at=None):
        """Create and publish an announcement"""
        announcement = Announcement.objects.create(
            title=title,
            content=content,
            author=author,
            is_global=is_global,
            target_roles=target_roles or [],
            expires_at=expires_at
        )
        announcement.publish()
        
        # Notify all active users
        from django.contrib.auth import get_user_model
        User = get_user_model()
        users = User.objects.filter(is_active=True)
        
        NotificationService.send_bulk_notification(
            users=users,
            notification_type='announcement',
            title=f"New Announcement: {title}",
            message=content[:200],
            action_url=f'/communications/announcements/{announcement.id}/'
        )
        
        return announcement
    
    @staticmethod
    def get_recent_announcements(limit=5):
        """Get recent published announcements"""
        return Announcement.objects.filter(
            is_published=True
        ).order_by('-published_at')[:limit]
