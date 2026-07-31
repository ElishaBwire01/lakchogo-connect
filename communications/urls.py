from django.urls import path
from . import views

app_name = 'communications'

urlpatterns = [
    # Notifications
    path('notifications/', views.notification_list, name='notification_list'),
    path('notifications/<int:notification_id>/', views.notification_detail, name='notification_detail'),
    path('notifications/<int:notification_id>/read/', views.mark_notification_read, name='mark_read'),
    path('notifications/<int:notification_id>/delete/', views.delete_notification, name='delete_notification'),
    path('notifications/mark-all-read/', views.mark_all_read, name='mark_all_read'),
    path('notifications/unread-count/', views.get_unread_count, name='unread_count'),
    path('notifications/unread-count-json/', views.get_unread_count_json, name='unread_count_json'),
    path('notifications/badge/', views.notification_badge, name='notification_badge'),
    
    # Announcements
    path('announcements/', views.announcement_list, name='announcement_list'),
    path('announcements/<int:announcement_id>/', views.announcement_detail, name='announcement_detail'),
    path('announcements/create/', views.announcement_create, name='announcement_create'),
    
    # Chat
    path('chat/', views.chat_dashboard, name='chat_dashboard'),
    path('chat/<int:room_id>/', views.chat_room, name='chat_room'),
    path('chat/send/<int:room_id>/', views.send_chat_message, name='send_message'),
    path('chat/create/', views.create_chat_room, name='create_room'),
    path('chat/direct/<int:user_id>/', views.create_direct_chat, name='create_direct_chat'),
    path('chat/message/<int:message_id>/delete/', views.delete_chat_message, name='delete_message'),
    path('chat/unread-count/', views.get_unread_chat_count, name='unread_chat_count'),
    path('chat/<int:room_id>/details/', views.chat_room_details, name='chat_room_details'),
]
