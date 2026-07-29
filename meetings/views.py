from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Meeting

@login_required
def index(request):
    meetings = Meeting.objects.all().order_by('-date')
    context = {
        'title': 'Meetings',
        'meetings': meetings,
    }
    return render(request, 'meetings/index.html', context)

@login_required
def schedule(request):
    context = {'title': 'Schedule Meeting'}
    return render(request, 'meetings/schedule.html', context)

@login_required
def meeting_detail(request, meeting_id):
    meeting = get_object_or_404(Meeting, id=meeting_id)
    context = {
        'title': meeting.title,
        'meeting': meeting,
    }
    return render(request, 'meetings/detail.html', context)

@login_required
def take_attendance(request, meeting_id):
    meeting = get_object_or_404(Meeting, id=meeting_id)
    context = {
        'title': f'Attendance - {meeting.title}',
        'meeting': meeting,
    }
    return render(request, 'meetings/attendance.html', context)
