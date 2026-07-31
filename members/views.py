from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.db.models import Q
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.utils import timezone
from .models import Member, MemberNote, MemberDocument, MemberContributionSummary
from accounts.decorators import admin_required, committee_required, permission_required

User = get_user_model()

@login_required
def list_members(request):
    """List all members - All authenticated users can view"""
    members = Member.objects.all().order_by('-date_joined')
    
    status_filter = request.GET.get('status')
    if status_filter:
        members = members.filter(status=status_filter)
    
    query = request.GET.get('q')
    if query:
        members = members.filter(
            Q(user__first_name__icontains=query) |
            Q(user__last_name__icontains=query) |
            Q(user__phone__icontains=query) |
            Q(member_id__icontains=query)
        )
    
    paginator = Paginator(members, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'members': page_obj,
        'title': 'Members',
        'status_filter': status_filter,
        'query': query,
        'total_members': Member.objects.count(),
        'active_members': Member.objects.filter(status='active').count(),
    }
    return render(request, 'members/list.html', context)


@login_required
@permission_required('can_add_member')
def register_member(request):
    """Register a new member - Requires add member permission"""
    if request.method == 'POST':
        username = request.POST.get('username')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        phone = request.POST.get('phone')
        id_number = request.POST.get('id_number')
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists.')
            return render(request, 'members/register.html', {'title': 'Register Member'})
        
        if User.objects.filter(phone=phone).exists():
            messages.error(request, 'Phone number already exists.')
            return render(request, 'members/register.html', {'title': 'Register Member'})
        
        if User.objects.filter(id_number=id_number).exists():
            messages.error(request, 'ID number already exists.')
            return render(request, 'members/register.html', {'title': 'Register Member'})
        
        user = User.objects.create_user(
            username=username,
            first_name=first_name,
            last_name=last_name,
            phone=phone,
            id_number=id_number,
            email=email,
            password=password
        )
        
        member = Member.objects.create(
            user=user,
            next_of_kin_name=request.POST.get('next_of_kin_name', ''),
            next_of_kin_phone=request.POST.get('next_of_kin_phone', ''),
            next_of_kin_relationship=request.POST.get('next_of_kin_relationship', ''),
            status='active'
        )
        
        MemberContributionSummary.objects.create(member=member)
        
        messages.success(request, f'Member {member.get_full_name()} registered successfully! Member ID: {member.member_id}')
        return redirect('members:detail', member_id=member.member_id)
    
    context = {'title': 'Register Member'}
    return render(request, 'members/register.html', context)


@login_required
def member_detail(request, member_id):
    """View member details - All authenticated users can view"""
    member = get_object_or_404(Member, member_id=member_id)
    notes = member.member_notes_list.all().order_by('-created_at')[:10]
    
    try:
        summary = member.contribution_summary
    except MemberContributionSummary.DoesNotExist:
        summary = MemberContributionSummary.objects.create(member=member)
        summary.update_summary()
    
    context = {
        'member': member,
        'notes': notes,
        'summary': summary,
        'title': f'Member: {member.get_full_name()}',
    }
    return render(request, 'members/detail.html', context)


@login_required
@permission_required('can_edit_member')
def edit_member(request, member_id):
    """Edit member details - Requires edit permission"""
    member = get_object_or_404(Member, member_id=member_id)
    
    if request.method == 'POST':
        user = member.user
        user.first_name = request.POST.get('first_name')
        user.last_name = request.POST.get('last_name')
        user.phone = request.POST.get('phone')
        user.email = request.POST.get('email')
        user.save()
        
        member.date_of_birth = request.POST.get('date_of_birth') or None
        member.gender = request.POST.get('gender')
        member.occupation = request.POST.get('occupation')
        member.address = request.POST.get('address')
        
        member.next_of_kin_name = request.POST.get('next_of_kin_name', '')
        member.next_of_kin_phone = request.POST.get('next_of_kin_phone', '')
        member.next_of_kin_relationship = request.POST.get('next_of_kin_relationship', '')
        member.next_of_kin_address = request.POST.get('next_of_kin_address', '')
        
        member.emergency_contact_name = request.POST.get('emergency_contact_name', '')
        member.emergency_contact_phone = request.POST.get('emergency_contact_phone', '')
        member.emergency_contact_relationship = request.POST.get('emergency_contact_relationship', '')
        
        member.status = request.POST.get('status', 'active')
        member.notes = request.POST.get('notes', '')
        member.save()
        
        messages.success(request, 'Member updated successfully!')
        return redirect('members:detail', member_id=member.member_id)
    
    context = {
        'member': member,
        'title': f'Edit Member: {member.get_full_name()}',
    }
    return render(request, 'members/edit.html', context)


@login_required
def search_members(request):
    """Search members - All authenticated users can search"""
    query = request.GET.get('q', '')
    members = Member.objects.filter(status='active')
    
    if query:
        members = members.filter(
            Q(user__first_name__icontains=query) |
            Q(user__last_name__icontains=query) |
            Q(user__phone__icontains=query) |
            Q(member_id__icontains=query)
        )
    
    context = {
        'members': members,
        'query': query,
        'title': 'Search Members',
    }
    return render(request, 'members/search.html', context)


@login_required
@permission_required('can_add_member')
def add_note(request, member_id):
    """Add a note to a member - Requires add permission"""
    member = get_object_or_404(Member, member_id=member_id)
    
    if request.method == 'POST':
        content = request.POST.get('content')
        is_private = request.POST.get('is_private') == 'on'
        
        if content:
            MemberNote.objects.create(
                member=member,
                author=request.user,
                content=content,
                is_private=is_private
            )
            messages.success(request, 'Note added successfully!')
        else:
            messages.error(request, 'Note content is required.')
        
        return redirect('members:detail', member_id=member.member_id)
    
    context = {
        'member': member,
        'title': 'Add Note',
    }
    return render(request, 'members/add_note.html', context)


@login_required
def member_status(request, member_id):
    """View member status - All authenticated users can view"""
    member = get_object_or_404(Member, member_id=member_id)
    try:
        summary = member.contribution_summary
    except MemberContributionSummary.DoesNotExist:
        summary = MemberContributionSummary.objects.create(member=member)
        summary.update_summary()
    
    context = {
        'member': member,
        'summary': summary,
        'title': f'Status: {member.get_full_name()}',
    }
    return render(request, 'members/status.html', context)

@login_required
@permission_required('can_edit_member')
def update_status(request, member_id):
    """Update member status - Requires edit permission"""
    member = get_object_or_404(Member, member_id=member_id)
    
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in ['active', 'inactive', 'suspended', 'pending']:
            member.status = new_status
            member.save()
            messages.success(request, f'Member status updated to {new_status}.')
        else:
            messages.error(request, 'Invalid status.')
        
        return redirect('members:detail', member_id=member.member_id)
    
    context = {
        'member': member,
        'title': 'Update Status',
    }
    return render(request, 'members/update_status.html', context)

@login_required
def get_member_json(request, member_id):
    """Get member data as JSON for API"""
    member = get_object_or_404(Member, member_id=member_id)
    
    data = {
        'member_id': member.member_id,
        'name': member.get_full_name(),
        'phone': member.user.phone,
        'email': member.user.email,
        'status': member.status,
        'compliance_status': member.compliance_status,
        'date_joined': member.date_joined.isoformat(),
    }
    return JsonResponse(data)


@login_required
def get_members_json(request):
    """Get all members as JSON for API"""
    members = Member.objects.filter(status='active')
    data = []
    
    for member in members:
        data.append({
            'member_id': member.member_id,
            'name': member.get_full_name(),
            'phone': member.user.phone,
            'status': member.status,
        })
    
    return JsonResponse({'members': data})
