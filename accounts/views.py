from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.conf import settings
import random
from .models import User, Role, UserRole, UserActivityLog
from .forms import UserRegistrationForm, UserLoginForm, UserProfileForm, RoleForm
from communications.services import NotificationTriggers

User = get_user_model()

def register(request):
    """User registration view"""
    if request.user.is_authenticated:
        return redirect('dashboard:index')
    
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
        
        if User.objects.filter(id_number=id_number).exists():
            messages.error(request, 'ID number already registered.')
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
        
        # Assign default role
        default_role = Role.objects.filter(is_default=True).first()
        if default_role:
            UserRole.objects.create(user=user, role=default_role)
        
        # Log activity
        UserActivityLog.objects.create(
            user=user,
            action='CREATE',
            description='User registered',
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT', '')
        )
        
        # Create member (if not already created by signal)
        from members.models import Member, MemberContributionSummary
        try:
            member = Member.objects.create(
                user=user,
                status='active'
            )
            # Create contribution summary
            MemberContributionSummary.objects.create(member=member)
            
            # Send welcome notifications
            NotificationTriggers.member_registered(member)
            
        except Exception as e:
            print(f"Error creating member: {e}")
        
        messages.success(request, f'Account created successfully! Welcome {user.get_full_name()}')
        return redirect('accounts:login')
    
    return render(request, 'accounts/register.html')


def user_login(request):
    """User login view"""
    if request.user.is_authenticated:
        return redirect('dashboard:index')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            if user.is_active:
                login(request, user)
                
                # Log login activity
                UserActivityLog.objects.create(
                    user=user,
                    action='LOGIN',
                    description='User logged in',
                    ip_address=request.META.get('REMOTE_ADDR'),
                    user_agent=request.META.get('HTTP_USER_AGENT', '')
                )
                
                messages.success(request, f'Welcome back, {user.get_full_name()}!')
                next_url = request.GET.get('next', 'dashboard:index')
                return redirect(next_url)
            else:
                messages.error(request, 'Your account is inactive.')
        else:
            messages.error(request, 'Invalid username or password.')
    
    return render(request, 'accounts/login.html')


@login_required
def user_logout(request):
    """User logout view"""
    if request.user.is_authenticated:
        UserActivityLog.objects.create(
            user=request.user,
            action='LOGOUT',
            description='User logged out',
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT', '')
        )
        logout(request)
    messages.info(request, 'You have been logged out successfully.')
    return redirect('accounts:login')


@login_required
def profile(request):
    """User profile view"""
    return render(request, 'accounts/profile.html', {'user': request.user})


@login_required
def profile_edit(request):
    """Edit user profile"""
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
    """Password reset view"""
    if request.method == 'POST':
        phone = request.POST.get('phone')
        try:
            user = User.objects.get(phone=phone)
            reset_code = random.randint(100000, 999999)
            request.session['reset_code'] = reset_code
            request.session['reset_user_id'] = user.id
            
            # In production, send SMS via Africa's Talking
            messages.success(request, f'Password reset code sent to {phone}. Check your phone.')
            return redirect('accounts:password_reset_confirm')
        except User.DoesNotExist:
            messages.error(request, 'No user found with that phone number.')
    
    return render(request, 'accounts/password_reset.html')


def password_reset_confirm(request):
    """Confirm password reset"""
    if request.method == 'POST':
        code = request.POST.get('code')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        
        if new_password != confirm_password:
            messages.error(request, 'Passwords do not match.')
            return render(request, 'accounts/password_reset_confirm.html')
        
        saved_code = request.session.get('reset_code')
        user_id = request.session.get('reset_user_id')
        
        if saved_code and user_id and int(code) == saved_code:
            user = get_object_or_404(User, id=user_id)
            user.set_password(new_password)
            user.save()
            
            del request.session['reset_code']
            del request.session['reset_user_id']
            
            messages.success(request, 'Password reset successful! Please login.')
            return redirect('accounts:login')
        else:
            messages.error(request, 'Invalid reset code.')
    
    return render(request, 'accounts/password_reset_confirm.html')


# Admin views
@login_required
def manage_users(request):
    """User management for admins"""
    users = User.objects.all().order_by('-date_joined')
    
    is_admin = request.user.is_superuser or UserRole.objects.filter(
        user=request.user,
        role__name='Admin',
        is_active=True
    ).exists()
    
    if not is_admin:
        messages.error(request, 'You do not have permission to manage users.')
        return redirect('dashboard:index')
    
    return render(request, 'accounts/manage_users.html', {'users': users})


@login_required
def manage_roles(request):
    """Role management for admins"""
    is_admin = request.user.is_superuser or UserRole.objects.filter(
        user=request.user,
        role__name='Admin',
        is_active=True
    ).exists()
    
    if not is_admin:
        messages.error(request, 'You do not have permission to manage roles.')
        return redirect('dashboard:index')
    
    roles = Role.objects.all()
    return render(request, 'accounts/manage_roles.html', {'roles': roles})


@login_required
def create_role(request):
    """Create new role"""
    is_admin = request.user.is_superuser or UserRole.objects.filter(
        user=request.user,
        role__name='Admin',
        is_active=True
    ).exists()
    
    if not is_admin:
        messages.error(request, 'You do not have permission to create roles.')
        return redirect('dashboard:index')
    
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        is_default = request.POST.get('is_default') == 'on'
        
        if Role.objects.filter(name=name).exists():
            messages.error(request, 'Role with this name already exists.')
            return render(request, 'accounts/create_role.html')
        
        role = Role.objects.create(
            name=name,
            description=description,
            is_default=is_default
        )
        messages.success(request, f'Role "{name}" created successfully!')
        return redirect('accounts:manage_roles')
    
    return render(request, 'accounts/create_role.html')


@login_required
def assign_role(request, user_id):
    """Assign role to user"""
    is_admin = request.user.is_superuser or UserRole.objects.filter(
        user=request.user,
        role__name='Admin',
        is_active=True
    ).exists()
    
    if not is_admin:
        messages.error(request, 'You do not have permission to assign roles.')
        return redirect('dashboard:index')
    
    user = get_object_or_404(User, id=user_id)
    
    if request.method == 'POST':
        role_id = request.POST.get('role_id')
        role = get_object_or_404(Role, id=role_id)
        
        UserRole.objects.filter(user=user, is_active=True).update(is_active=False)
        
        UserRole.objects.create(
            user=user,
            role=role,
            assigned_by=request.user
        )
        
        messages.success(request, f'Role "{role.name}" assigned to {user.get_full_name()}')
        return redirect('accounts:manage_users')
    
    roles = Role.objects.all()
    return render(request, 'accounts/assign_role.html', {'user': user, 'roles': roles})


@login_required
def toggle_user_status(request, user_id):
    """Activate/deactivate user"""
    is_admin = request.user.is_superuser or UserRole.objects.filter(
        user=request.user,
        role__name='Admin',
        is_active=True
    ).exists()
    
    if not is_admin:
        messages.error(request, 'You do not have permission to manage users.')
        return redirect('dashboard:index')
    
    user = get_object_or_404(User, id=user_id)
    if user == request.user:
        messages.error(request, 'You cannot deactivate yourself.')
    else:
        user.is_active = not user.is_active
        user.save()
        status = 'activated' if user.is_active else 'deactivated'
        messages.success(request, f'User {user.get_full_name()} {status}.')
    
    return redirect('accounts:manage_users')


def get_user_roles(request, user_id):
    """API: Get user roles"""
    try:
        user = get_object_or_404(User, id=user_id)
        roles = UserRole.objects.filter(user=user, is_active=True).select_related('role')
        data = [{'id': ur.role.id, 'name': ur.role.name} for ur in roles]
        return JsonResponse({'roles': data})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


def check_username(request):
    """API: Check if username exists"""
    username = request.GET.get('username')
    if username:
        exists = User.objects.filter(username=username).exists()
        return JsonResponse({'exists': exists})
    return JsonResponse({'error': 'Username required'}, status=400)


@login_required
def dashboard(request):
    """User dashboard redirect"""
    return redirect('dashboard:index')
