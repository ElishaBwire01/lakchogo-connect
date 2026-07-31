from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from django.core.paginator import Paginator
from django.db.models import Q
from django.contrib.auth import get_user_model
from .models import Notification, Announcement, ChatRoom, ChatMessage, MeetingRoom
from .services import NotificationService, NotificationTriggers
from datetime import datetime
import random
import hashlib
import time

User = get_user_model()

# ============================================
# NOTIFICATION VIEWS
# ============================================

@login_required
def notification_list(request):
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
    count = NotificationService.mark_all_read(request.user)
    messages.success(request, f'Marked {count} notifications as read.')
    return redirect('communications:notification_list')


@login_required
def get_unread_count(request):
    count = NotificationService.get_unread_count(request.user)
    return JsonResponse({'unread_count': count})


@login_required
def get_unread_count_json(request):
    count = NotificationService.get_unread_count(request.user)
    return JsonResponse({'unread_count': count})


@login_required
def notification_badge(request):
    count = NotificationService.get_unread_count(request.user)
    return render(request, 'communications/notifications/badge.html', {'unread_count': count})


# ============================================
# ANNOUNCEMENT VIEWS
# ============================================

@login_required
def announcement_list(request):
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
    chat_rooms = ChatRoom.objects.filter(
        members=request.user,
        is_active=True
    ).order_by('-last_message_time')
    
    for room in chat_rooms:
        room.unread_count = room.get_unread_count(request.user)
    
    users = User.objects.filter(is_active=True).exclude(id=request.user.id)
    
    context = {
        'chat_rooms': chat_rooms,
        'users': users,
        'title': 'Chat',
    }
    return render(request, 'communications/chat/dashboard.html', context)


@login_required
def chat_room(request, room_id):
    room = get_object_or_404(ChatRoom, id=room_id, is_active=True)
    
    if not room.members.filter(id=request.user.id).exists():
        messages.error(request, 'You are not a member of this chat room.')
        return redirect('communications:chat_dashboard')
    
    messages_list = ChatMessage.objects.filter(
        room=room,
        is_deleted=False
    ).exclude(
        message_type='system'
    ).select_related('sender').order_by('created_at')
    
    context = {
        'room': room,
        'messages': messages_list,
        'members': room.members.all(),
        'title': room.name or f'Chat Room {room.id}',
    }
    return render(request, 'communications/chat/room.html', context)


@login_required
def send_chat_message(request, room_id):
    room = get_object_or_404(ChatRoom, id=room_id)
    
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Invalid method'}, status=400)
    
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
    if request.method == 'POST':
        room_name = request.POST.get('name', '')
        room_type = request.POST.get('room_type', 'group')
        member_ids = request.POST.getlist('member_ids')
        
        if not member_ids:
            messages.error(request, 'Please select at least one member.')
            return redirect('communications:chat_dashboard')
        
        members = [request.user]
        for user_id in member_ids:
            try:
                user = User.objects.get(id=user_id)
                members.append(user)
            except User.DoesNotExist:
                pass
        
        if room_type == 'group':
            member_ids_sorted = sorted([str(m.id) for m in members])
            existing_rooms = ChatRoom.objects.filter(room_type='group', is_active=True)
            for room in existing_rooms:
                room_members = list(room.members.all().values_list('id', flat=True))
                if sorted(room_members) == sorted([m.id for m in members]):
                    messages.info(request, 'A group chat with these members already exists.')
                    return redirect('communications:chat_room', room_id=room.id)
        
        room = ChatRoom.objects.create(
            name=room_name or f"Group Chat",
            room_type=room_type,
            created_by=request.user,
            is_active=True
        )
        
        room.members.add(*members)
        
        messages.success(request, 'Chat room created successfully!')
        return redirect('communications:chat_room', room_id=room.id)
    
    return redirect('communications:chat_dashboard')


@login_required
def create_direct_chat(request, user_id):
    other_user = get_object_or_404(User, id=user_id, is_active=True)
    
    rooms = ChatRoom.objects.filter(room_type='direct', is_active=True)
    for room in rooms:
        members = room.members.all()
        if members.count() == 2 and request.user in members and other_user in members:
            return redirect('communications:chat_room', room_id=room.id)
    
    room = ChatRoom.objects.create(
        name=f"Chat with {other_user.get_full_name()}",
        room_type='direct',
        created_by=request.user,
        is_active=True
    )
    room.members.add(request.user, other_user)
    
    return redirect('communications:chat_room', room_id=room.id)


@login_required
def chat_room_details(request, room_id):
    room = get_object_or_404(ChatRoom, id=room_id)
    
    if not room.members.filter(id=request.user.id).exists():
        return JsonResponse({'status': 'error', 'message': 'Access denied'}, status=403)
    
    messages_list = ChatMessage.objects.filter(
        room=room,
        is_deleted=False
    ).exclude(
        message_type='system'
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
            for m in messages_list
        ]
    }
    return JsonResponse(data)


@login_required
def delete_chat_message(request, message_id):
    message = get_object_or_404(ChatMessage, id=message_id)
    
    if message.sender != request.user and not request.user.is_staff:
        return JsonResponse({'status': 'error', 'message': 'Permission denied'}, status=403)
    
    message.soft_delete()
    return JsonResponse({'status': 'success'})


@login_required
def get_unread_chat_count(request):
    rooms = ChatRoom.objects.filter(members=request.user, is_active=True)
    total_unread = sum([room.get_unread_count(request.user) for room in rooms])
    return JsonResponse({'unread_count': total_unread})


@login_required
def clear_chat(request, room_id):
    room = get_object_or_404(ChatRoom, id=room_id)
    
    if not room.members.filter(id=request.user.id).exists():
        messages.error(request, 'You are not a member of this chat room.')
        return redirect('communications:chat_dashboard')
    
    if request.method == 'POST':
        ChatMessage.objects.filter(room=room).delete()
        messages.success(request, 'Chat cleared successfully!')
        return redirect('communications:chat_room', room_id=room.id)
    
    context = {
        'room': room,
        'title': 'Clear Chat',
    }
    return render(request, 'communications/chat/clear.html', context)


@login_required
def room_list(request):
    rooms = ChatRoom.objects.filter(members=request.user, is_active=True)
    data = {
        'rooms': [
            {'id': room.id, 'name': room.name or f'Chat {room.id}'}
            for room in rooms
        ]
    }
    return JsonResponse(data)


@login_required
def edit_message(request, message_id):
    message = get_object_or_404(ChatMessage, id=message_id)
    
    if message.sender != request.user:
        return JsonResponse({'status': 'error', 'message': 'You can only edit your own messages'}, status=403)
    
    if request.method == 'POST':
        content = request.POST.get('content')
        if not content:
            return JsonResponse({'status': 'error', 'message': 'Content is required'}, status=400)
        
        message.content = content
        message.save()
        
        return JsonResponse({
            'status': 'success',
            'message': {
                'id': message.id,
                'content': message.content,
                'updated_at': message.updated_at.strftime('%Y-%m-%d %H:%M:%S')
            }
        })
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)


@login_required
def forward_message(request, message_id):
    message = get_object_or_404(ChatMessage, id=message_id)
    
    if request.method == 'POST':
        room_id = request.POST.get('room_id')
        target_room = get_object_or_404(ChatRoom, id=room_id)
        
        if not target_room.members.filter(id=request.user.id).exists():
            return JsonResponse({'status': 'error', 'message': 'You are not a member of that chat'}, status=403)
        
        forwarded = ChatMessage.objects.create(
            room=target_room,
            sender=request.user,
            message_type='text',
            content=f"📩 Forwarded from {message.sender.get_full_name()}: {message.content}"
        )
        
        return JsonResponse({
            'status': 'success',
            'message': 'Message forwarded successfully'
        })
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)


@login_required
def share_message(request, message_id):
    message = get_object_or_404(ChatMessage, id=message_id)
    
    share_url = request.build_absolute_uri(f'/communications/chat/{message.room.id}/#message-{message.id}')
    
    return JsonResponse({
        'status': 'success',
        'share_url': share_url,
        'message': message.content,
        'sender': message.sender.get_full_name()
    })


@login_required
def reply_to_message(request, message_id):
    message = get_object_or_404(ChatMessage, id=message_id)
    
    if request.method == 'POST':
        content = request.POST.get('content')
        if not content:
            return JsonResponse({'status': 'error', 'message': 'Content is required'}, status=400)
        
        reply = ChatMessage.objects.create(
            room=message.room,
            sender=request.user,
            message_type='text',
            content=f"📩 Replying to {message.sender.get_full_name()}: {message.content[:50]}...\n\n{content}"
        )
        
        return JsonResponse({
            'status': 'success',
            'message': {
                'id': reply.id,
                'content': reply.content,
                'created_at': reply.created_at.strftime('%Y-%m-%d %H:%M:%S')
            }
        })
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)


# ============================================
# MEETING ROOM VIEWS
# ============================================

def generate_jitsi_room_id(name, creator_username):
    name_slug = name.lower().replace(' ', '-')[:20]
    name_slug = ''.join(c if c.isalnum() or c == '-' else '-' for c in name_slug)
    
    creator = creator_username[:10] if creator_username else 'host'
    creator = ''.join(c if c.isalnum() else '-' for c in creator)
    
    timestamp = str(int(time.time()))[-6:]
    hash_input = f"{name}{creator}{timestamp}{random.randint(1000, 9999)}"
    hash_suffix = hashlib.md5(hash_input.encode()).hexdigest()[:6]
    
    room_id = f"{name_slug}-{creator}-{timestamp}-{hash_suffix}"
    room_id = room_id[:50]
    
    if not room_id[-1].isalnum():
        room_id = room_id[:-1] + '0'
    
    return room_id


@login_required
def create_meeting_room(request, chat_room_id=None):
    chat_room = None
    if chat_room_id:
        chat_room = get_object_or_404(ChatRoom, id=chat_room_id)
        
        if not chat_room.members.filter(id=request.user.id).exists():
            messages.error(request, 'You are not a member of this chat room.')
            return redirect('communications:chat_dashboard')
    
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        scheduled_start_str = request.POST.get('scheduled_start')
        scheduled_end_str = request.POST.get('scheduled_end')
        attendee_ids = request.POST.getlist('attendee_ids')
        send_notifications = request.POST.get('send_notifications') == 'on'
        
        if not name:
            messages.error(request, 'Meeting name is required.')
            return render(request, 'communications/meeting/create.html', {
                'chat_room': chat_room,
                'users': User.objects.filter(is_active=True).exclude(id=request.user.id)
            })
        
        scheduled_start = None
        scheduled_end = None
        
        if scheduled_start_str:
            try:
                scheduled_start = datetime.strptime(scheduled_start_str, '%Y-%m-%dT%H:%M')
                scheduled_start = timezone.make_aware(scheduled_start)
            except ValueError:
                pass
        
        if scheduled_end_str:
            try:
                scheduled_end = datetime.strptime(scheduled_end_str, '%Y-%m-%dT%H:%M')
                scheduled_end = timezone.make_aware(scheduled_end)
            except ValueError:
                pass
        
        meeting = MeetingRoom.objects.create(
            name=name,
            description=description,
            chat_room=chat_room,
            created_by=request.user,
            scheduled_start=scheduled_start,
            scheduled_end=scheduled_end,
            status='active'
        )
        
        if attendee_ids:
            users = User.objects.filter(id__in=attendee_ids)
            meeting.attendees.add(*users)
        elif chat_room:
            meeting.attendees.add(*chat_room.members.all())
        
        if send_notifications:
            notification_count = 0
            date_str = "Schedule TBD"
            if meeting.scheduled_start:
                try:
                    date_str = meeting.scheduled_start.strftime("%B %d, %Y at %H:%M")
                except:
                    date_str = str(meeting.scheduled_start)
            
            for attendee in meeting.attendees.all():
                if attendee != request.user:
                    Notification.create_notification(
                        recipient=attendee,
                        notification_type='meeting_scheduled',
                        title=f'🎥 Video Meeting Invitation: {meeting.name}',
                        message=f'{request.user.get_full_name()} has invited you to a video meeting: {meeting.name}\n'
                               f'📅 {date_str}\n'
                               f'🔑 Join URL: {meeting.meeting_url}\n'
                               f'📝 {meeting.description[:100] if meeting.description else "No description"}',
                        action_url=f'/communications/meeting/{meeting.id}/',
                        related_id=meeting.id,
                        related_model='MeetingRoom',
                        priority='high'
                    )
                    notification_count += 1
            
            messages.success(request, f'Meeting "{meeting.name}" created successfully! {notification_count} notifications sent.')
        else:
            messages.success(request, f'Meeting "{meeting.name}" created successfully!')
        
        return redirect('communications:meeting_room', meeting_id=meeting.id)
    
    name_slug = 'meeting'
    creator = request.user.username[:10]
    timestamp = str(int(time.time()))[-6:]
    hash_suffix = hashlib.md5(f"{name_slug}{creator}{timestamp}{random.randint(1000, 9999)}".encode()).hexdigest()[:6]
    auto_meeting_id = f"{name_slug}-{creator}-{timestamp}-{hash_suffix}"
    
    users = User.objects.filter(is_active=True).exclude(id=request.user.id)
    
    context = {
        'title': 'Create Video Meeting',
        'chat_room': chat_room,
        'users': users,
        'auto_meeting_id': auto_meeting_id,
        'jitsi_domain': 'meet.jit.si',
    }
    return render(request, 'communications/meeting/create.html', context)


@login_required
def meeting_room(request, meeting_id):
    meeting = get_object_or_404(MeetingRoom, id=meeting_id)
    
    if not meeting.attendees.filter(id=request.user.id).exists() and meeting.created_by != request.user:
        messages.error(request, 'You are not invited to this meeting.')
        return redirect('communications:chat_dashboard')
    
    context = {
        'title': f'Meeting: {meeting.name}',
        'meeting': meeting,
        'attendees': meeting.attendees.all(),
    }
    return render(request, 'communications/meeting/room.html', context)


@login_required
def meeting_list(request):
    meetings = MeetingRoom.objects.filter(
        Q(attendees=request.user) | Q(created_by=request.user),
        status='active'
    ).distinct().order_by('-created_at')
    
    paginator = Paginator(meetings, 10)
    page = request.GET.get('page')
    meetings_page = paginator.get_page(page)
    
    context = {
        'title': 'My Meetings',
        'meetings': meetings_page,
    }
    return render(request, 'communications/meeting/list.html', context)


@login_required
def join_meeting(request, meeting_id):
    meeting = get_object_or_404(MeetingRoom, id=meeting_id)
    
    if not meeting.attendees.filter(id=request.user.id).exists() and meeting.created_by != request.user:
        messages.error(request, 'You are not invited to this meeting.')
        return redirect('communications:chat_dashboard')
    
    if not meeting.attendees.filter(id=request.user.id).exists():
        meeting.attendees.add(request.user)
    
    meeting_url = meeting.get_meeting_link(request.user)
    
    return redirect(meeting_url)


@login_required
def end_meeting(request, meeting_id):
    meeting = get_object_or_404(MeetingRoom, id=meeting_id)
    
    if meeting.created_by != request.user:
        messages.error(request, 'Only the meeting creator can end the meeting.')
        return redirect('communications:meeting_room', meeting_id=meeting.id)
    
    if request.method == 'POST':
        meeting.status = 'ended'
        meeting.is_active = False
        meeting.save()
        
        for attendee in meeting.attendees.all():
            if attendee != request.user:
                Notification.create_notification(
                    recipient=attendee,
                    notification_type='meeting_cancelled',
                    title=f'📢 Meeting Ended: {meeting.name}',
                    message=f'The meeting "{meeting.name}" has been ended by {request.user.get_full_name()}.',
                    action_url='/communications/meetings/',
                    related_id=meeting.id,
                    related_model='MeetingRoom',
                    priority='high'
                )
        
        messages.success(request, 'Meeting ended successfully.')
        return redirect('communications:meeting_list')
    
    context = {
        'meeting': meeting,
        'title': f'End Meeting: {meeting.name}',
    }
    return render(request, 'communications/meeting/end.html', context)


@login_required
def send_meeting_reminder(request, meeting_id):
    meeting = get_object_or_404(MeetingRoom, id=meeting_id)
    
    if meeting.created_by != request.user:
        messages.error(request, 'Only the meeting creator can send reminders.')
        return redirect('communications:meeting_room', meeting_id=meeting.id)
    
    if request.method == 'POST':
        reminder_count = 0
        date_str = "soon"
        if meeting.scheduled_start:
            try:
                date_str = meeting.scheduled_start.strftime("%B %d, %Y at %H:%M")
            except:
                date_str = str(meeting.scheduled_start)
        
        for attendee in meeting.attendees.all():
            if attendee != request.user:
                Notification.create_notification(
                    recipient=attendee,
                    notification_type='meeting_reminder',
                    title=f'⏰ Reminder: {meeting.name}',
                    message=f'Reminder: Your meeting "{meeting.name}" is scheduled for {date_str}.',
                    action_url=f'/communications/meeting/{meeting.id}/',
                    related_id=meeting.id,
                    related_model='MeetingRoom',
                    priority='high'
                )
                reminder_count += 1
        
        messages.success(request, f'Reminders sent to {reminder_count} attendees!')
        return redirect('communications:meeting_room', meeting_id=meeting.id)
    
    context = {
        'meeting': meeting,
        'title': f'Send Reminder: {meeting.name}',
    }
    return render(request, 'communications/meeting/send_reminder.html', context)
