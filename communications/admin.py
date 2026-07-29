from django.contrib import admin
from .models import Notification, Announcement, ChatRoom, ChatMessage

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('title', 'recipient', 'notification_type', 'status', 'created_at')
    list_filter = ('notification_type', 'status', 'channel', 'created_at')
    search_fields = ('title', 'message', 'recipient__username', 'recipient__phone')
    raw_id_fields = ('recipient',)
    readonly_fields = ('sent_at', 'read_at')
    date_hierarchy = 'created_at'

@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'is_published', 'published_at', 'is_global')
    list_filter = ('is_published', 'is_global', 'created_at')
    search_fields = ('title', 'content', 'author__username')
    date_hierarchy = 'created_at'

@admin.register(ChatRoom)
class ChatRoomAdmin(admin.ModelAdmin):
    list_display = ('name', 'room_type', 'is_active', 'created_by', 'created_at')
    list_filter = ('room_type', 'is_active', 'created_at')
    search_fields = ('name', 'created_by__username')
    filter_horizontal = ('members',)

@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ('room', 'sender', 'message_type', 'content_preview', 'created_at')
    list_filter = ('message_type', 'is_announcement', 'is_deleted', 'created_at')
    search_fields = ('content', 'sender__username')
    raw_id_fields = ('room', 'sender')
    
    def content_preview(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    content_preview.short_description = 'Content'
