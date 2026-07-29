from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Notification, Announcement, ChatRoom, ChatMessage

User = get_user_model()

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = [
            'id', 'recipient', 'notification_type', 'title', 'message',
            'channel', 'status', 'action_url', 'sent_at', 'read_at',
            'is_announcement', 'priority', 'created_at'
        ]
        read_only_fields = ['id', 'created_at', 'sent_at', 'read_at']

class AnnouncementSerializer(serializers.ModelSerializer):
    author_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Announcement
        fields = [
            'id', 'title', 'content', 'author', 'author_name',
            'is_published', 'published_at', 'expires_at',
            'target_roles', 'is_global', 'created_at'
        ]
        read_only_fields = ['id', 'created_at', 'published_at']
    
    def get_author_name(self, obj):
        return obj.author.get_full_name()

class ChatMessageSerializer(serializers.ModelSerializer):
    sender_name = serializers.SerializerMethodField()
    
    class Meta:
        model = ChatMessage
        fields = [
            'id', 'room', 'sender', 'sender_name', 'message_type',
            'content', 'file_attachment', 'is_announcement',
            'is_deleted', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']
    
    def get_sender_name(self, obj):
        return obj.sender.get_full_name()

class ChatRoomSerializer(serializers.ModelSerializer):
    members_count = serializers.SerializerMethodField()
    last_message = ChatMessageSerializer(read_only=True)
    
    class Meta:
        model = ChatRoom
        fields = [
            'id', 'name', 'room_type', 'members', 'members_count',
            'is_active', 'created_by', 'last_message', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']
    
    def get_members_count(self, obj):
        return obj.members.count()
