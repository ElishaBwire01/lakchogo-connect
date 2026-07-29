from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.contrib.auth import get_user_model

User = get_user_model()

def register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        phone = request.POST.get('phone')
        id_number = request.POST.get('id_number')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        
        if password1 != password2:
            messages.error(request, 'Passwords do not match.')
            return render(request, 'accounts/register.html')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists.')
            return render(request, 'accounts/register.html')
        
        if User.objects.filter(phone=phone).exists():
            messages.error(request, 'Phone number already registered.')
            return render(request, 'accounts/register.html')
        
        user = User.objects.create_user(
            username=username,
            first_name=first_name,
            last_name=last_name,
            phone=phone,
            id_number=id_number,
            email=email,
            password=password1
        )
        messages.success(request, 'Registration successful! Please login.')
        return redirect('accounts:login')
    
    return render(request, 'accounts/register.html')

def user_login(request):
    if request.user.is_authenticated:
        return redirect('dashboard:index')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            next_url = request.GET.get('next', 'dashboard:index')
            return redirect(next_url)
        else:
            messages.error(request, 'Invalid username or password.')
    
    return render(request, 'accounts/login.html')

def user_logout(request):
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('accounts:login')

@login_required
def profile(request):
    return render(request, 'accounts/profile.html', {'user': request.user})

@login_required
def profile_edit(request):
    if request.method == 'POST':
        user = request.user
        user.first_name = request.POST.get('first_name')
        user.last_name = request.POST.get('last_name')
        user.phone = request.POST.get('phone')
        user.email = request.POST.get('email')
        user.save()
        messages.success(request, 'Profile updated successfully!')
        return redirect('accounts:profile')
    
    return render(request, 'accounts/profile_edit.html', {'user': request.user})

def password_reset(request):
    return render(request, 'accounts/password_reset.html')

def password_reset_confirm(request):
    return render(request, 'accounts/password_reset_confirm.html')

@login_required
def manage_users(request):
    users = User.objects.all()
    return render(request, 'accounts/manage_users.html', {'users': users})

@login_required
def manage_roles(request):
    return render(request, 'accounts/manage_roles.html')

@login_required
def create_role(request):
    return render(request, 'accounts/create_role.html')

@login_required
def assign_role(request, user_id):
    return render(request, 'accounts/assign_role.html')

@login_required
def toggle_user_status(request, user_id):
    return redirect('accounts:manage_users')

def get_user_roles(request, user_id):
    return JsonResponse({'roles': []})

def check_username(request):
    return JsonResponse({'exists': False})
