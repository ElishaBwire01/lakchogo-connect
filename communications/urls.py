from django.urls import path
from . import views

app_name = 'communications'

urlpatterns = [
    # Notifications
    path('notifications/', views.notification_list, name='notification_list'),
    path('notifications/<int:notification_id>/', views.notification_detail, name='notification_detail'),
    path('notifications/<int:notification_id>/read/', views.mark_notification_read, name='mark_read'),
    path('notifications/<int:notification_id>/delete/', views.delete_notification, name='delete_notification'),
    path('notifications/unread-count/', views.get_unread_count, name='unread_count'),
    
    # Announcements
    path('announcements/', views.announcement_list, name='announcement_list'),
    path('announcements/<int:announcement_id>/', views.announcement_detail, name='announcement_detail'),
    path('announcements/create/', views.announcement_create, name='announcement_create'),
    
    # Chat
    path('chat/', views.chat_dashboard, name='chat_dashboard'),
    path('chat/<int:room_id>/', views.chat_room, name='chat_room'),
    path('chat/send/<int:room_id>/', views.send_chat_message, name='send_message'),
    path('chat/create/', views.create_chat_room, name='create_room'),
]
