from django.contrib import admin
from .models import Notification, Announcement, ChatRoom, ChatMessage, MeetingRoom

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('id', 'created_at')
    search_fields = ('id',)
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-created_at',)

@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ('id', 'created_at')
    search_fields = ('id',)
    ordering = ('-created_at',)

@admin.register(ChatRoom)
class ChatRoomAdmin(admin.ModelAdmin):
    list_display = ('id', 'created_at')
    search_fields = ('id',)
    ordering = ('-created_at',)

@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'created_at')
    search_fields = ('id',)
    ordering = ('created_at',)

@admin.register(MeetingRoom)
class MeetingRoomAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'room_code', 'status', 'created_at')
    list_filter = ('status',)
    search_fields = ('name', 'room_code')
    readonly_fields = ('room_code', 'meeting_url', 'created_at', 'updated_at')
    ordering = ('-created_at',)
