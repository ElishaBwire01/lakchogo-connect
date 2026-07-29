from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.db import models
from .models import Member

User = get_user_model()

@login_required
def list_members(request):
    members = Member.objects.filter(status='active')
    context = {
        'members': members,
        'title': 'Members',
    }
    return render(request, 'members/list.html', context)

@login_required
def register_member(request):
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
            return render(request, 'members/register.html')
        
        if User.objects.filter(phone=phone).exists():
            messages.error(request, 'Phone number already exists.')
            return render(request, 'members/register.html')
        
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
        )
        
        messages.success(request, f'Member {member.get_full_name()} registered successfully!')
        return redirect('members:list')
    
    return render(request, 'members/register.html', {'title': 'Register Member'})

@login_required
def member_detail(request, member_id):
    member = get_object_or_404(Member, member_id=member_id)
    context = {
        'member': member,
        'title': f'Member: {member.get_full_name()}',
    }
    return render(request, 'members/detail.html', context)

@login_required
def edit_member(request, member_id):
    member = get_object_or_404(Member, member_id=member_id)
    if request.method == 'POST':
        user = member.user
        user.first_name = request.POST.get('first_name')
        user.last_name = request.POST.get('last_name')
        user.phone = request.POST.get('phone')
        user.email = request.POST.get('email')
        user.save()
        
        member.next_of_kin_name = request.POST.get('next_of_kin_name', '')
        member.next_of_kin_phone = request.POST.get('next_of_kin_phone', '')
        member.next_of_kin_relationship = request.POST.get('next_of_kin_relationship', '')
        member.status = request.POST.get('status', 'active')
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
    query = request.GET.get('q', '')
    members = Member.objects.filter(status='active')
    if query:
        members = members.filter(
            models.Q(user__first_name__icontains=query) |
            models.Q(user__last_name__icontains=query) |
            models.Q(user__phone__icontains=query) |
            models.Q(member_id__icontains=query)
        )
    context = {
        'members': members,
        'query': query,
        'title': 'Search Members',
    }
    return render(request, 'members/search.html', context)
