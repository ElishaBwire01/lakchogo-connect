from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from django.core.paginator import Paginator
from django.db.models import Q
from django.contrib.auth import get_user_model
from .models import Notification, Announcement, ChatRoom, ChatMessage
from .services import NotificationService, NotificationTriggers

User = get_user_model()

# ============================================
# NOTIFICATION VIEWS
# ============================================

@login_required
def notification_list(request):
    """Display all notifications for the logged-in user"""
    notifications = Notification.objects.filter(
        recipient=request.user
    ).order_by('-created_at')
    
    if request.GET.get('mark_all_read'):
        NotificationService.mark_all_read(request.user)
        messages.success(request, 'All notifications marked as read.')
        return redirect('communications:notification_list')
    
    paginator = Paginator(notifications, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'notifications': page_obj,
        'unread_count': NotificationService.get_unread_count(request.user),
        'title': 'Notifications',
    }
    return render(request, 'communications/notifications/list.html', context)


@login_required
def notification_detail(request, notification_id):
    """View a single notification"""
    notification = get_object_or_404(
        Notification, 
        id=notification_id, 
        recipient=request.user
    )
    
    if notification.status in ['pending', 'sent']:
        notification.mark_as_read()
    
    context = {
        'notification': notification,
        'title': 'Notification Detail',
    }
    return render(request, 'communications/notifications/detail.html', context)


@login_required
def mark_notification_read(request, notification_id):
    """Mark a single notification as read (AJAX)"""
    try:
        notification = get_object_or_404(
            Notification, 
            id=notification_id, 
            recipient=request.user
        )
        notification.mark_as_read()
        return JsonResponse({'status': 'success', 'message': 'Notification marked as read'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)


@login_required
def delete_notification(request, notification_id):
    """Delete a notification"""
    try:
        notification = get_object_or_404(
            Notification, 
            id=notification_id, 
            recipient=request.user
        )
        notification.delete()
        return JsonResponse({'status': 'success'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)


@login_required
def mark_all_read(request):
    """Mark all notifications as read"""
    count = NotificationService.mark_all_read(request.user)
    messages.success(request, f'Marked {count} notifications as read.')
    return redirect('communications:notification_list')


@login_required
def get_unread_count(request):
    """Get unread notification count"""
    count = NotificationService.get_unread_count(request.user)
    return JsonResponse({'unread_count': count})


@login_required
def notification_badge(request):
    """Render notification badge for navbar"""
    count = NotificationService.get_unread_count(request.user)
    return render(request, 'communications/notifications/badge.html', {'unread_count': count})


# ============================================
# ANNOUNCEMENT VIEWS
# ============================================

@login_required
def announcement_list(request):
    """Display all announcements"""
    announcements = Announcement.objects.filter(
        is_published=True
    ).order_by('-published_at')
    
    paginator = Paginator(announcements, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'announcements': page_obj,
        'title': 'Announcements',
    }
    return render(request, 'communications/announcements/list.html', context)


@login_required
def announcement_detail(request, announcement_id):
    """View a single announcement"""
    announcement = get_object_or_404(
        Announcement, 
        id=announcement_id,
        is_published=True
    )
    context = {
        'announcement': announcement,
        'title': announcement.title,
    }
    return render(request, 'communications/announcements/detail.html', context)


@login_required
def announcement_create(request):
    """Create a new announcement"""
    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        is_global = request.POST.get('is_global') == 'on'
        
        announcement = Announcement.objects.create(
            title=title,
            content=content,
            author=request.user,
            is_global=is_global
        )
        announcement.publish()
        
        messages.success(request, 'Announcement published successfully!')
        return redirect('communications:announcement_list')
    
    context = {
        'title': 'Create Announcement',
    }
    return render(request, 'communications/announcements/create.html', context)


# ============================================
# CHAT VIEWS
# ============================================

@login_required
def chat_dashboard(request):
    """Chat dashboard showing all rooms"""
    # Get all rooms the user is a member of
    chat_rooms = ChatRoom.objects.filter(
        members=request.user,
        is_active=True
    ).order_by('-last_message_time')
    
    # Get unread counts for each room
    for room in chat_rooms:
        room.unread_count = room.get_unread_count(request.user)
    
    # Get all users for creating new chat
    users = User.objects.filter(is_active=True).exclude(id=request.user.id)
    
    context = {
        'chat_rooms': chat_rooms,
        'users': users,
        'title': 'Chat',
    }
    return render(request, 'communications/chat/dashboard.html', context)


@login_required
def chat_room(request, room_id):
    """View a specific chat room"""
    room = get_object_or_404(ChatRoom, id=room_id, is_active=True)
    
    # Check if user is a member
    if not room.members.filter(id=request.user.id).exists():
        messages.error(request, 'You are not a member of this chat room.')
        return redirect('communications:chat_dashboard')
    
    # Get messages for this room
    messages_list = ChatMessage.objects.filter(
        room=room,
        is_deleted=False
    ).select_related('sender').order_by('created_at')
    
    # Mark messages as read (simplified)
    # In production, you'd use a read receipt model
    
    context = {
        'room': room,
        'messages': messages_list,
        'members': room.members.all(),
        'title': room.name or f'Chat Room {room.id}',
    }
    return render(request, 'communications/chat/room.html', context)


@login_required
def send_chat_message(request, room_id):
    """Send a chat message"""
    room = get_object_or_404(ChatRoom, id=room_id)
    
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Invalid method'}, status=400)
    
    # Check if user is a member
    if not room.members.filter(id=request.user.id).exists():
        return JsonResponse({'status': 'error', 'message': 'Not a member'}, status=403)
    
    content = request.POST.get('content')
    message_type = request.POST.get('message_type', 'text')
    
    if not content:
        return JsonResponse({'status': 'error', 'message': 'Message content is required'}, status=400)
    
    message = ChatMessage.objects.create(
        room=room,
        sender=request.user,
        message_type=message_type,
        content=content
    )
    
    return JsonResponse({
        'status': 'success',
        'message': {
            'id': message.id,
            'sender': request.user.username,
            'sender_name': request.user.get_full_name(),
            'content': message.content,
            'created_at': message.created_at.strftime('%Y-%m-%d %H:%M:%S')
        }
    })


@login_required
def create_chat_room(request):
    """Create a new chat room"""
    if request.method == 'POST':
        room_name = request.POST.get('name', '')
        room_type = request.POST.get('room_type', 'group')
        member_ids = request.POST.getlist('member_ids')
        
        # Validate members
        if not member_ids:
            messages.error(request, 'Please select at least one member.')
            return redirect('communications:chat_dashboard')
        
        # Include the creator
        members = [request.user]
        for user_id in member_ids:
            try:
                user = User.objects.get(id=user_id)
                members.append(user)
            except User.DoesNotExist:
                pass
        
        # Check if a group chat already exists with same members
        if room_type == 'group':
            # Sort member ids for consistent comparison
            member_ids_sorted = sorted([str(m.id) for m in members])
            # Look for existing room with same members
            existing_rooms = ChatRoom.objects.filter(room_type='group', is_active=True)
            for room in existing_rooms:
                room_members = list(room.members.all().values_list('id', flat=True))
                if sorted(room_members) == sorted([m.id for m in members]):
                    messages.info(request, 'A group chat with these members already exists.')
                    return redirect('communications:chat_room', room_id=room.id)
        
        # Create room
        room = ChatRoom.objects.create(
            name=room_name or f"Group Chat",
            room_type=room_type,
            created_by=request.user,
            is_active=True
        )
        
        # Add members
        room.members.add(*members)
        
        # Create system message
        ChatMessage.objects.create(
            room=room,
            sender=request.user,
            message_type='system',
            content=f'Chat created by {request.user.get_full_name()}'
        )
        
        messages.success(request, 'Chat room created successfully!')
        return redirect('communications:chat_room', room_id=room.id)
    
    return redirect('communications:chat_dashboard')


@login_required
def create_direct_chat(request, user_id):
    """Create or get a direct chat with a specific user"""
    other_user = get_object_or_404(User, id=user_id, is_active=True)
    
    # Check if direct chat already exists
    # Find room where both users are members and room_type is 'direct'
    rooms = ChatRoom.objects.filter(room_type='direct', is_active=True)
    for room in rooms:
        members = room.members.all()
        if members.count() == 2 and request.user in members and other_user in members:
            return redirect('communications:chat_room', room_id=room.id)
    
    # Create new direct chat
    room = ChatRoom.objects.create(
        name=f"Chat with {other_user.get_full_name()}",
        room_type='direct',
        created_by=request.user,
        is_active=True
    )
    room.members.add(request.user, other_user)
    
    # Create system message
    ChatMessage.objects.create(
        room=room,
        sender=request.user,
        message_type='system',
        content=f'Direct chat started'
    )
    
    return redirect('communications:chat_room', room_id=room.id)


@login_required
def chat_room_details(request, room_id):
    """Get chat room details as JSON for AJAX"""
    room = get_object_or_404(ChatRoom, id=room_id)
    
    if not room.members.filter(id=request.user.id).exists():
        return JsonResponse({'status': 'error', 'message': 'Access denied'}, status=403)
    
    messages = ChatMessage.objects.filter(
        room=room,
        is_deleted=False
    ).select_related('sender').order_by('created_at')
    
    data = {
        'id': room.id,
        'name': room.name,
        'members': [{'id': m.id, 'name': m.get_full_name()} for m in room.members.all()],
        'messages': [
            {
                'id': m.id,
                'sender': m.sender.username,
                'sender_name': m.sender.get_full_name(),
                'content': m.content,
                'created_at': m.created_at.strftime('%Y-%m-%d %H:%M:%S')
            }
            for m in messages
        ]
    }
    return JsonResponse(data)


@login_required
def delete_chat_message(request, message_id):
    """Delete a chat message (soft delete)"""
    message = get_object_or_404(ChatMessage, id=message_id)
    
    # Only sender or admin can delete
    if message.sender != request.user and not request.user.is_staff:
        return JsonResponse({'status': 'error', 'message': 'Permission denied'}, status=403)
    
    message.soft_delete()
    return JsonResponse({'status': 'success'})


@login_required
def get_unread_chat_count(request):
    """Get total unread chat messages count for the user"""
    rooms = ChatRoom.objects.filter(members=request.user, is_active=True)
    total_unread = sum([room.get_unread_count(request.user) for room in rooms])
    return JsonResponse({'unread_count': total_unread})

@login_required
def get_unread_count_json(request):
    """Get unread notification count as JSON for AJAX"""
    from .services import NotificationService
    count = NotificationService.get_unread_count(request.user)
    return JsonResponse({'unread_count': count})

@login_required
def get_unread_count_json(request):
    """Get unread notification count as JSON for AJAX"""
    from .services import NotificationService
    count = NotificationService.get_unread_count(request.user)
    return JsonResponse({'unread_count': count})

@login_required
def get_unread_chat_count(request):
    """Get unread chat messages count for the user"""
    from .models import ChatRoom
    rooms = ChatRoom.objects.filter(members=request.user, is_active=True)
    total_unread = sum([room.get_unread_count(request.user) for room in rooms])
    return JsonResponse({'unread_count': total_unread})
