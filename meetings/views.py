from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.utils import timezone
from django.http import JsonResponse, HttpResponse
from django.db.models import Q
from .models import Meeting, Attendance, MeetingMinutes
from members.models import Member
import json
import hashlib

# Try to import qrcode, fallback if not installed
try:
    import qrcode
    from io import BytesIO
    QRCODE_AVAILABLE = True
except ImportError:
    QRCODE_AVAILABLE = False

@login_required
def index(request):
    """List all meetings"""
    meetings = Meeting.objects.all().order_by('-date')
    
    status_filter = request.GET.get('status')
    if status_filter:
        meetings = meetings.filter(status=status_filter)
    
    query = request.GET.get('q')
    if query:
        meetings = meetings.filter(
            Q(title__icontains=query) |
            Q(venue__icontains=query) |
            Q(description__icontains=query)
        )
    
    paginator = Paginator(meetings, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'meetings': page_obj,
        'title': 'Meetings',
        'status_filter': status_filter,
        'query': query,
    }
    return render(request, 'meetings/index.html', context)


@login_required
def schedule(request):
    """Schedule a new meeting"""
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        date = request.POST.get('date')
        venue = request.POST.get('venue')
        agenda = request.POST.get('agenda')
        
        if not all([title, date, venue]):
            messages.error(request, 'Title, Date, and Venue are required.')
            return render(request, 'meetings/schedule.html', {'title': 'Schedule Meeting'})
        
        meeting = Meeting.objects.create(
            title=title,
            description=description,
            date=date,
            venue=venue,
            agenda=agenda,
            created_by=request.user,
            status='scheduled'
        )
        
        messages.success(request, f'Meeting "{title}" scheduled successfully!')
        return redirect('meetings:detail', meeting_id=meeting.id)
    
    context = {
        'title': 'Schedule Meeting',
        'now': timezone.now().strftime('%Y-%m-%dT%H:%M'),
    }
    return render(request, 'meetings/schedule.html', context)


@login_required
def detail(request, meeting_id):
    """View meeting details"""
    meeting = get_object_or_404(Meeting, id=meeting_id)
    attendees = Attendance.objects.filter(meeting=meeting)
    
    context = {
        'meeting': meeting,
        'attendees': attendees,
        'title': meeting.title,
        'present_count': attendees.filter(status='present').count(),
        'absent_count': attendees.filter(status='absent').count(),
        'excused_count': attendees.filter(status='excused').count(),
        'total_members': Member.objects.filter(status='active').count(),
    }
    return render(request, 'meetings/detail.html', context)


@login_required
def take_attendance(request, meeting_id):
    """Take attendance for a meeting"""
    meeting = get_object_or_404(Meeting, id=meeting_id)
    
    if meeting.status == 'cancelled':
        messages.error(request, 'This meeting has been cancelled.')
        return redirect('meetings:detail', meeting_id=meeting.id)
    
    members = Member.objects.filter(status='active')
    
    if request.method == 'POST':
        for member in members:
            status = request.POST.get(f'attendance_{member.id}')
            if status:
                attendance, created = Attendance.objects.get_or_create(
                    meeting=meeting,
                    member=member,
                    defaults={
                        'status': status,
                        'recorded_by': request.user,
                        'check_in_method': 'manual',
                    }
                )
                if not created:
                    attendance.status = status
                    attendance.save()
        
        if request.POST.get('complete_meeting'):
            meeting.status = 'completed'
            meeting.save()
            messages.success(request, 'Meeting marked as completed.')
        
        messages.success(request, 'Attendance recorded successfully!')
        return redirect('meetings:detail', meeting_id=meeting.id)
    
    context = {
        'meeting': meeting,
        'members': members,
        'title': f'Take Attendance - {meeting.title}',
    }
    return render(request, 'meetings/attendance.html', context)


@login_required
def upload_minutes(request, meeting_id):
    """Upload minutes for a meeting"""
    meeting = get_object_or_404(Meeting, id=meeting_id)
    
    if request.method == 'POST':
        minutes_text = request.POST.get('minutes_text')
        summary = request.POST.get('summary')
        file = request.FILES.get('file')
        
        minutes, created = MeetingMinutes.objects.get_or_create(
            meeting=meeting,
            defaults={
                'content': minutes_text or '',
                'summary': summary or '',
                'attendees_count': meeting.get_attendance_count(),
            }
        )
        
        if not created:
            minutes.content = minutes_text or minutes.content
            minutes.summary = summary or minutes.summary
            if file:
                minutes.file_attachment = file
            minutes.save()
        
        meeting.minutes_text = minutes_text
        meeting.save()
        
        messages.success(request, 'Meeting minutes uploaded successfully!')
        return redirect('meetings:detail', meeting_id=meeting.id)
    
    context = {
        'meeting': meeting,
        'title': f'Upload Minutes - {meeting.title}',
    }
    return render(request, 'meetings/upload_minutes.html', context)


@login_required
def edit_meeting(request, meeting_id):
    """Edit meeting details"""
    meeting = get_object_or_404(Meeting, id=meeting_id)
    
    if request.method == 'POST':
        meeting.title = request.POST.get('title')
        meeting.description = request.POST.get('description')
        meeting.date = request.POST.get('date')
        meeting.venue = request.POST.get('venue')
        meeting.agenda = request.POST.get('agenda')
        meeting.status = request.POST.get('status')
        meeting.save()
        
        messages.success(request, 'Meeting updated successfully!')
        return redirect('meetings:detail', meeting_id=meeting.id)
    
    context = {
        'meeting': meeting,
        'title': f'Edit Meeting - {meeting.title}',
    }
    return render(request, 'meetings/edit.html', context)


@login_required
def delete_meeting(request, meeting_id):
    """Delete a meeting"""
    meeting = get_object_or_404(Meeting, id=meeting_id)
    
    if request.method == 'POST':
        meeting.delete()
        messages.success(request, 'Meeting deleted successfully!')
        return redirect('meetings:index')
    
    context = {
        'meeting': meeting,
        'title': f'Delete Meeting - {meeting.title}',
    }
    return render(request, 'meetings/delete.html', context)


@login_required
def generate_qr(request, meeting_id):
    """Generate QR code data for a meeting (JSON response)"""
    meeting = get_object_or_404(Meeting, id=meeting_id)
    
    data = {
        'meeting_id': meeting.id,
        'title': meeting.title,
        'date': meeting.date.isoformat(),
        'venue': meeting.venue,
    }
    qr_data = json.dumps(data)
    qr_hash = hashlib.md5(qr_data.encode()).hexdigest()
    
    meeting.qr_code = qr_hash
    meeting.save()
    
    return JsonResponse({
        'qr_code': qr_hash,
        'meeting_id': meeting.id,
        'data': qr_data,
    })


@login_required
def generate_qr_image(request, meeting_id):
    """Generate QR code image for a meeting"""
    meeting = get_object_or_404(Meeting, id=meeting_id)
    
    if not QRCODE_AVAILABLE:
        # Fallback - create a simple text QR
        from django.http import HttpResponse
        data = json.dumps({
            'meeting_id': meeting.id,
            'title': meeting.title,
            'date': meeting.date.isoformat(),
            'venue': meeting.venue,
        })
        return HttpResponse(f"QR Code Data: {data}", content_type="text/plain")
    
    data = json.dumps({
        'meeting_id': meeting.id,
        'title': meeting.title,
        'date': meeting.date.isoformat(),
        'venue': meeting.venue,
    })
    
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    
    response = HttpResponse(content_type="image/png")
    img.save(response, "PNG")
    return response


@login_required
def qr_code_display(request, meeting_id):
    """Display QR code for a meeting"""
    meeting = get_object_or_404(Meeting, id=meeting_id)
    
    context = {
        'meeting': meeting,
        'qr_code_url': f"/meetings/{meeting.id}/qr-image/",
        'title': f'QR Code - {meeting.title}',
        'qrcode_available': QRCODE_AVAILABLE,
    }
    return render(request, 'meetings/qr_code.html', context)


@login_required
def qr_check_in(request, meeting_id):
    """Check-in via QR code"""
    meeting = get_object_or_404(Meeting, id=meeting_id)
    
    if request.method == 'POST':
        member_id = request.POST.get('member_id')
        qr_code = request.POST.get('qr_code')
        
        if qr_code != meeting.qr_code:
            return JsonResponse({'status': 'error', 'message': 'Invalid QR code'})
        
        member = get_object_or_404(Member, member_id=member_id)
        
        attendance, created = Attendance.objects.get_or_create(
            meeting=meeting,
            member=member,
            defaults={
                'status': 'present',
                'check_in_method': 'qr',
                'check_in_time': timezone.now(),
                'recorded_by': request.user,
            }
        )
        
        if not created:
            attendance.status = 'present'
            attendance.check_in_time = timezone.now()
            attendance.save()
        
        return JsonResponse({
            'status': 'success',
            'member': member.get_full_name(),
            'time': timezone.now().isoformat(),
        })
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})


@login_required
def get_attendance_summary(request, meeting_id):
    """Get attendance summary as JSON"""
    meeting = get_object_or_404(Meeting, id=meeting_id)
    attendance = Attendance.objects.filter(meeting=meeting)
    
    data = {
        'meeting_id': meeting.id,
        'meeting_title': meeting.title,
        'total_attendees': attendance.count(),
        'present': attendance.filter(status='present').count(),
        'absent': attendance.filter(status='absent').count(),
        'excused': attendance.filter(status='excused').count(),
        'late': attendance.filter(status='late').count(),
    }
    return JsonResponse(data)

@login_required
def qr_code_display(request, meeting_id):
    """Display QR code for a meeting - HTML page"""
    meeting = get_object_or_404(Meeting, id=meeting_id)
    
    context = {
        'meeting': meeting,
        'qr_image_url': f"/meetings/{meeting.id}/qr-image/",
        'qr_data_url': f"/meetings/{meeting.id}/qr-data/",
        'title': f'QR Code - {meeting.title}',
        'qrcode_available': QRCODE_AVAILABLE,
    }
    return render(request, 'meetings/qr_code.html', context)

@login_required
def generate_qr(request, meeting_id):
    """Generate QR code data for a meeting (JSON response for API)"""
    meeting = get_object_or_404(Meeting, id=meeting_id)
    
    data = {
        'meeting_id': meeting.id,
        'title': meeting.title,
        'date': meeting.date.isoformat(),
        'venue': meeting.venue,
    }
    qr_data = json.dumps(data)
    qr_hash = hashlib.md5(qr_data.encode()).hexdigest()
    
    meeting.qr_code = qr_hash
    meeting.save()
    
    return JsonResponse({
        'qr_code': qr_hash,
        'meeting_id': meeting.id,
        'data': qr_data,
    })

@login_required
def generate_qr_image(request, meeting_id):
    """Generate QR code image for a meeting (PNG)"""
    import qrcode
    from io import BytesIO
    import json
    
    meeting = get_object_or_404(Meeting, id=meeting_id)
    
    # Create QR code data
    data = json.dumps({
        'meeting_id': meeting.id,
        'title': meeting.title,
        'date': meeting.date.isoformat(),
        'venue': meeting.venue,
    })
    
    # Generate QR code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Save to response
    response = HttpResponse(content_type="image/png")
    img.save(response, "PNG")
    return response


@login_required
def generate_qr_json(request, meeting_id):
    """Generate QR code data as JSON"""
    meeting = get_object_or_404(Meeting, id=meeting_id)
    import json
    import hashlib
    
    data = {
        'meeting_id': meeting.id,
        'title': meeting.title,
        'date': meeting.date.isoformat(),
        'venue': meeting.venue,
    }
    qr_data = json.dumps(data)
    qr_hash = hashlib.md5(qr_data.encode()).hexdigest()
    
    meeting.qr_code = qr_hash
    meeting.save()
    
    return JsonResponse({
        'qr_code': qr_hash,
        'meeting_id': meeting.id,
        'data': qr_data,
    })


@login_required
def qr_code_display(request, meeting_id):
    """Display QR code page"""
    meeting = get_object_or_404(Meeting, id=meeting_id)
    
    context = {
        'meeting': meeting,
        'qr_image_url': f"/meetings/{meeting.id}/qr-image/",
        'title': f'QR Code - {meeting.title}',
    }
    return render(request, 'meetings/qr_code.html', context)
