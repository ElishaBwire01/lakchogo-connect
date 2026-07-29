from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import BereavementEvent

@login_required
def index(request):
    events = BereavementEvent.objects.filter(status='active')
    context = {
        'title': 'Welfare',
        'events': events,
    }
    return render(request, 'welfare/index.html', context)

@login_required
def create_event(request):
    context = {'title': 'Create Welfare Event'}
    return render(request, 'welfare/create.html', context)

@login_required
def event_detail(request, event_id):
    event = get_object_or_404(BereavementEvent, id=event_id)
    context = {
        'title': f'Event: {event.deceased_name}',
        'event': event,
    }
    return render(request, 'welfare/detail.html', context)
