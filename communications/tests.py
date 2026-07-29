from django.test import TestCase
from django.contrib.auth import get_user_model
from .models import Notification, Announcement, ChatRoom, ChatMessage
from .services import NotificationService, AnnouncementService

User = get_user_model()

class NotificationModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            phone='+254712345678',
            password='TestPassword123'
        )
    
    def test_create_notification(self):
        notification = Notification.objects.create(
            recipient=self.user,
            notification_type='system',
            title='Test Notification',
            message='This is a test notification'
        )
        self.assertEqual(notification.title, 'Test Notification')
        self.assertEqual(notification.status, 'pending')
        self.assertEqual(str(notification), 'Test Notification - testuser')
    
    def test_mark_notification_read(self):
        notification = Notification.objects.create(
            recipient=self.user,
            notification_type='system',
            title='Test Notification',
            message='Test message'
        )
        notification.mark_as_read()
        self.assertEqual(notification.status, 'read')
        self.assertIsNotNone(notification.read_at)

class ChatModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            phone='+254712345678',
            password='TestPassword123'
        )
        self.room = ChatRoom.objects.create(
            name='Test Room',
            room_type='group',
            created_by=self.user
        )
    
    def test_create_chat_room(self):
        self.assertEqual(self.room.name, 'Test Room')
        self.assertEqual(self.room.room_type, 'group')
        self.assertEqual(str(self.room), 'Test Room')
    
    def test_create_chat_message(self):
        message = ChatMessage.objects.create(
            room=self.room,
            sender=self.user,
            content='Hello, this is a test message'
        )
        self.assertEqual(message.content, 'Hello, this is a test message')
        self.assertEqual(str(message), 'testuser: Hello, this is a test message')
