from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.db.models import Sum, Q
from django.utils import timezone
from .models import BereavementEvent, BereavementContribution, WelfareFund, WelfareRequest
from members.models import Member

# role_required temporarily disabled - will be enabled when decorators are ready
# from accounts.decorators import role_required

@login_required
def index(request):
    """Welfare dashboard"""
    events = BereavementEvent.objects.filter(status='active')
    total_collected = BereavementEvent.objects.aggregate(
        total=Sum('amount_collected')
    )['total'] or 0
    
    total_target = BereavementEvent.objects.aggregate(
        total=Sum('collection_target')
    )['total'] or 0
    
    context = {
        'title': 'Welfare',
        'events': events,
        'total_collected': total_collected,
        'total_target': total_target,
        'active_events': events.count(),
        'total_events': BereavementEvent.objects.count(),
    }
    return render(request, 'welfare/index.html', context)


@login_required
def create_event(request):
    """Create a new bereavement event"""
    if request.method == 'POST':
        member_id = request.POST.get('member_id')
        deceased_name = request.POST.get('deceased_name')
        relationship = request.POST.get('relationship')
        date_of_death = request.POST.get('date_of_death')
        date_of_burial = request.POST.get('date_of_burial')
        collection_target = request.POST.get('collection_target')
        description = request.POST.get('description')
        
        if not all([member_id, deceased_name, relationship, date_of_death, collection_target]):
            messages.error(request, 'Please fill in all required fields.')
            return render(request, 'welfare/create.html', {'title': 'Create Event'})
        
        member = get_object_or_404(Member, member_id=member_id)
        
        event = BereavementEvent.objects.create(
            member=member,
            deceased_name=deceased_name,
            relationship=relationship,
            date_of_death=date_of_death,
            date_of_burial=date_of_burial or None,
            collection_target=collection_target,
            description=description,
            status='active'
        )
        
        messages.success(request, f'Bereavement event for {deceased_name} created successfully!')
        return redirect('welfare:detail', event_id=event.id)
    
    context = {
        'title': 'Create Welfare Event',
        'members': Member.objects.filter(status='active'),
    }
    return render(request, 'welfare/create.html', context)


@login_required
def detail(request, event_id):
    """View event details"""
    event = get_object_or_404(BereavementEvent, id=event_id)
    contributions = event.contributions.all().order_by('-created_at')
    
    # Get contribution stats
    total_contributors = contributions.values('contributor').distinct().count()
    total_public = contributions.filter(is_public_contribution=True).count()
    
    context = {
        'title': f'Event: {event.deceased_name}',
        'event': event,
        'contributions': contributions,
        'total_contributors': total_contributors,
        'total_public': total_public,
        'progress': event.progress_percentage,
        'remaining': event.collection_target - event.amount_collected,
    }
    return render(request, 'welfare/detail.html', context)


@login_required
def add_contribution(request, event_id):
    """Add a contribution to an event"""
    event = get_object_or_404(BereavementEvent, id=event_id)
    
    if request.method == 'POST':
        contributor_id = request.POST.get('contributor_id')
        amount = request.POST.get('amount')
        payment_method = request.POST.get('payment_method')
        contributor_name = request.POST.get('contributor_name')
        contributor_phone = request.POST.get('contributor_phone')
        is_public = request.POST.get('is_public') == 'on'
        notes = request.POST.get('notes')
        
        if not amount:
            messages.error(request, 'Amount is required.')
            return redirect('welfare:detail', event_id=event.id)
        
        contributor = None
        if contributor_id:
            contributor = get_object_or_404(Member, id=contributor_id)
        
        contribution = BereavementContribution.objects.create(
            event=event,
            contributor=contributor,
            amount=amount,
            payment_method=payment_method or 'cash',
            is_public_contribution=is_public,
            contributor_name=contributor_name or (contributor.get_full_name() if contributor else ''),
            contributor_phone=contributor_phone or (contributor.user.phone if contributor else ''),
            notes=notes,
            recorded_by=request.user
        )
        
        # Update event amount collected
        event.amount_collected += float(amount)
        event.save()
        
        messages.success(request, f'Contribution of KES {amount} added successfully!')
        return redirect('welfare:detail', event_id=event.id)
    
    context = {
        'event': event,
        'members': Member.objects.filter(status='active'),
        'title': 'Add Contribution',
    }
    return render(request, 'welfare/add_contribution.html', context)


@login_required
def approve_event(request, event_id):
    """Approve/close a bereavement event"""
    event = get_object_or_404(BereavementEvent, id=event_id)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'close':
            event.close()
            messages.success(request, f'Event {event.event_code} closed successfully.')
        elif action == 'disburse':
            amount = request.POST.get('amount')
            notes = request.POST.get('notes')
            event.disburse(amount=amount, notes=notes)
            messages.success(request, f'Event {event.event_code} disbursed successfully.')
        
        return redirect('welfare:detail', event_id=event.id)
    
    context = {
        'event': event,
        'title': f'Approve/Close Event: {event.deceased_name}',
    }
    return render(request, 'welfare/approve.html', context)


@login_required
def list_events(request):
    """List all bereavement events"""
    events = BereavementEvent.objects.all().order_by('-created_at')
    
    status_filter = request.GET.get('status')
    if status_filter:
        events = events.filter(status=status_filter)
    
    paginator = Paginator(events, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'events': page_obj,
        'title': 'All Events',
        'status_filter': status_filter,
    }
    return render(request, 'welfare/list.html', context)


@login_required
def welfare_funds(request):
    """Manage welfare funds"""
    funds = WelfareFund.objects.filter(is_active=True)
    
    context = {
        'funds': funds,
        'title': 'Welfare Funds',
        'total_balance': funds.aggregate(total=Sum('balance'))['total'] or 0,
    }
    return render(request, 'welfare/funds.html', context)


@login_required
def welfare_requests(request):
    """Manage welfare requests"""
    requests = WelfareRequest.objects.all().order_by('-created_at')
    
    status_filter = request.GET.get('status')
    if status_filter:
        requests = requests.filter(status=status_filter)
    
    context = {
        'requests': requests,
        'title': 'Welfare Requests',
        'status_filter': status_filter,
    }
    return render(request, 'welfare/requests.html', context)


@login_required
def create_request(request):
    """Create a welfare request"""
    if request.method == 'POST':
        request_type = request.POST.get('request_type')
        title = request.POST.get('title')
        description = request.POST.get('description')
        amount_requested = request.POST.get('amount_requested')
        
        welfare_request = WelfareRequest.objects.create(
            member=request.user.member,
            request_type=request_type,
            title=title,
            description=description,
            amount_requested=amount_requested,
        )
        
        messages.success(request, 'Welfare request submitted successfully!')
        return redirect('welfare:requests')
    
    context = {
        'title': 'Create Welfare Request',
    }
    return render(request, 'welfare/create_request.html', context)


@login_required
def request_detail(request, request_id):
    """View welfare request details"""
    welfare_request = get_object_or_404(WelfareRequest, id=request_id)
    
    context = {
        'request': welfare_request,
        'title': f'Request: {welfare_request.title}',
    }
    return render(request, 'welfare/request_detail.html', context)


@login_required
def approve_request(request, request_id):
    """Approve a welfare request - simplified without role_required"""
    welfare_request = get_object_or_404(WelfareRequest, id=request_id)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        amount = request.POST.get('amount')
        notes = request.POST.get('notes')
        
        if action == 'approve':
            welfare_request.approve(request.user, amount)
            messages.success(request, 'Request approved successfully!')
        elif action == 'reject':
            welfare_request.reject(request.user, notes)
            messages.success(request, 'Request rejected.')
        elif action == 'disburse':
            welfare_request.disburse(request.user)
            messages.success(request, 'Request disbursed successfully!')
        
        return redirect('welfare:request_detail', request_id=welfare_request.id)
    
    context = {
        'request': welfare_request,
        'title': f'Review Request: {welfare_request.title}',
    }
    return render(request, 'welfare/approve_request.html', context)


@login_required
def get_event_stats(request, event_id):
    """Get event statistics as JSON"""
    event = get_object_or_404(BereavementEvent, id=event_id)
    contributions = event.contributions.all()
    
    data = {
        'event_code': event.event_code,
        'deceased_name': event.deceased_name,
        'collection_target': float(event.collection_target),
        'amount_collected': float(event.amount_collected),
        'progress': event.progress_percentage,
        'total_contributors': contributions.values('contributor').distinct().count(),
        'total_contributions': contributions.count(),
        'status': event.status,
    }
    return JsonResponse(data)
