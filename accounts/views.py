from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.utils import timezone
from django.db.models import Q
import random
import re
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
        
        default_role = Role.objects.filter(is_default=True).first()
        if default_role:
            UserRole.objects.create(user=user, role=default_role)
        
        UserActivityLog.objects.create(
            user=user,
            action='CREATE',
            description='User registered',
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT', '')
        )
        
        from members.models import Member, MemberContributionSummary
        try:
            member = Member.objects.create(
                user=user,
                status='active'
            )
            MemberContributionSummary.objects.create(member=member)
            
            try:
                send_welcome_email(user, member)
            except Exception as e:
                print(f"Welcome email error: {e}")
            
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


# ============================================
# PASSWORD RESET - ENHANCED FLOW
# ============================================

def password_reset(request):
    """Step 1: User enters phone number OR email address"""
    if request.method == 'POST':
        identifier = request.POST.get('identifier', '').strip()
        identifier_type = request.POST.get('identifier_type', 'phone')
        
        if not identifier:
            messages.error(request, 'Please enter your phone number or email address.')
            return render(request, 'accounts/password_reset.html')
        
        # Try to find user by phone or email
        if identifier_type == 'phone':
            phone_clean = identifier.replace(' ', '').replace('-', '').replace('(', '').replace(')', '')
            user = User.objects.filter(phone__icontains=phone_clean).first()
        else:
            user = User.objects.filter(email__iexact=identifier).first()
        
        if user:
            # Store user info in session
            request.session['reset_user_id'] = user.id
            request.session['reset_user_identifier'] = identifier
            request.session['reset_identifier_type'] = identifier_type
            
            # Show confirmation page - use redirect to ensure fresh page
            return redirect('accounts:password_reset_confirm_user')
        else:
            messages.error(request, f'No user found with that {identifier_type}. Please check and try again.')
            return render(request, 'accounts/password_reset.html')
    
    return render(request, 'accounts/password_reset.html')


def password_reset_confirm_user(request):
    """Step 2: User confirms identity, code sent to email"""
    user_id = request.session.get('reset_user_id')
    
    if not user_id:
        messages.error(request, 'Session expired. Please start over.')
        return redirect('accounts:password_reset')
    
    user = get_object_or_404(User, id=user_id)
    
    if request.method == 'POST':
        confirm = request.POST.get('confirm')
        
        if confirm == 'yes':
            # Generate reset code
            reset_code = random.randint(100000, 999999)
            request.session['reset_code'] = reset_code
            
            # Send email with reset code
            try:
                send_password_reset_email(user, reset_code)
                messages.success(request, f'✅ Password reset code sent to {user.email}')
            except Exception as e:
                print(f"Email error: {e}")
                messages.info(request, f'Reset code: {reset_code} (Check terminal)')
            
            # Notify admin about password reset request
            try:
                notify_admin_password_reset(user, reset_code)
            except Exception as e:
                print(f"Admin notification error: {e}")
            
            # Redirect to verification page
            return redirect('accounts:password_reset_verify')
        else:
            messages.info(request, 'Please confirm your identity to proceed.')
            return render(request, 'accounts/password_reset_confirm_user.html', {
                'user': user,
                'identifier': request.session.get('reset_user_identifier', '')
            })
    
    return render(request, 'accounts/password_reset_confirm_user.html', {
        'user': user,
        'identifier': request.session.get('reset_user_identifier', '')
    })


def password_reset_verify(request):
    """Step 3: User enters the verification code from email"""
    user_id = request.session.get('reset_user_id')
    
    if not user_id:
        messages.error(request, 'Session expired. Please start over.')
        return redirect('accounts:password_reset')
    
    user = get_object_or_404(User, id=user_id)
    
    if request.method == 'POST':
        code = request.POST.get('code', '').strip()
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        
        # Validate code is numeric
        if not code:
            messages.error(request, 'Please enter the verification code.')
            return render(request, 'accounts/password_reset_verify.html', {'user': user})
        
        if not code.isdigit():
            messages.error(request, 'Verification code must be a 6-digit number.')
            return render(request, 'accounts/password_reset_verify.html', {'user': user})
        
        if len(code) != 6:
            messages.error(request, 'Verification code must be exactly 6 digits.')
            return render(request, 'accounts/password_reset_verify.html', {'user': user})
        
        if not new_password or not confirm_password:
            messages.error(request, 'Please enter and confirm your new password.')
            return render(request, 'accounts/password_reset_verify.html', {'user': user})
        
        if new_password != confirm_password:
            messages.error(request, 'Passwords do not match.')
            return render(request, 'accounts/password_reset_verify.html', {'user': user})
        
        if len(new_password) < 8:
            messages.error(request, 'Password must be at least 8 characters.')
            return render(request, 'accounts/password_reset_verify.html', {'user': user})
        
        saved_code = request.session.get('reset_code')
        
        if saved_code and int(code) == saved_code:
            user.set_password(new_password)
            user.save()
            
            # Send confirmation email
            try:
                send_password_reset_confirmation(user)
            except Exception as e:
                print(f"Confirmation email error: {e}")
            
            # Notify admin about successful reset
            try:
                notify_admin_password_reset_success(user)
            except Exception as e:
                print(f"Admin success notification error: {e}")
            
            # Clear session
            request.session.pop('reset_code', None)
            request.session.pop('reset_user_id', None)
            request.session.pop('reset_user_identifier', None)
            request.session.pop('reset_identifier_type', None)
            
            messages.success(request, '✅ Password reset successful! Please login with your new password.')
            return redirect('accounts:login')
        else:
            messages.error(request, '❌ Invalid verification code. Please check your email and try again.')
    
    return render(request, 'accounts/password_reset_verify.html', {'user': user})


# ============================================
# ADMIN NOTIFICATION FUNCTIONS
# ============================================

def notify_admin_password_reset(user, reset_code):
    """Notify admin about password reset request"""
    admin_users = User.objects.filter(is_superuser=True)
    
    for admin in admin_users:
        subject = f'🔑 Password Reset Request - {user.get_full_name()}'
        html_content = render_to_string('emails/admin_password_reset_request.html', {
            'admin': admin,
            'user': user,
            'reset_code': reset_code,
            'timestamp': timezone.now().strftime('%Y-%m-%d %H:%M:%S'),
            'year': timezone.now().year
        })
        text_content = strip_tags(html_content)
        
        try:
            send_mail(
                subject,
                text_content,
                settings.DEFAULT_FROM_EMAIL,
                [admin.email],
                html_message=html_content,
                fail_silently=False
            )
        except Exception as e:
            print(f"Failed to send admin notification: {e}")


def notify_admin_password_reset_success(user):
    """Notify admin about successful password reset"""
    admin_users = User.objects.filter(is_superuser=True)
    
    for admin in admin_users:
        subject = f'✅ Password Reset Successful - {user.get_full_name()}'
        html_content = render_to_string('emails/admin_password_reset_success.html', {
            'admin': admin,
            'user': user,
            'timestamp': timezone.now().strftime('%Y-%m-%d %H:%M:%S'),
            'year': timezone.now().year
        })
        text_content = strip_tags(html_content)
        
        try:
            send_mail(
                subject,
                text_content,
                settings.DEFAULT_FROM_EMAIL,
                [admin.email],
                html_message=html_content,
                fail_silently=False
            )
        except Exception as e:
            print(f"Failed to send admin success notification: {e}")


# ============================================
# EMAIL FUNCTIONS FOR USERS
# ============================================

def send_welcome_email(user, member):
    """Send welcome email to new user"""
    subject = 'Welcome to LakChogo Connect!'
    html_content = render_to_string('emails/welcome.html', {
        'user': user,
        'member': member,
        'login_url': 'http://127.0.0.1:5000/accounts/login/',
        'year': timezone.now().year
    })
    text_content = strip_tags(html_content)
    
    send_mail(
        subject,
        text_content,
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        html_message=html_content,
        fail_silently=False
    )


def send_password_reset_email(user, reset_code):
    """Send password reset code via email"""
    subject = 'Password Reset - LakChogo Connect'
    
    html_content = render_to_string('emails/password_reset.html', {
        'user': user,
        'reset_code': reset_code,
        'reset_url': 'http://127.0.0.1:5000/accounts/password-reset/verify/',
        'year': timezone.now().year
    })
    text_content = strip_tags(html_content)
    
    send_mail(
        subject,
        text_content,
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        html_message=html_content,
        fail_silently=False
    )


def send_password_reset_confirmation(user):
    """Send confirmation email after password reset"""
    subject = 'Password Reset Confirmation - LakChogo Connect'
    
    html_content = render_to_string('emails/password_reset_confirmation.html', {
        'user': user,
        'login_url': 'http://127.0.0.1:5000/accounts/login/',
        'year': timezone.now().year
    })
    text_content = strip_tags(html_content)
    
    send_mail(
        subject,
        text_content,
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        html_message=html_content,
        fail_silently=False
    )


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

def google_login(request):
    """Redirect to Google OAuth login"""
    from django.shortcuts import redirect
    from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
    from allauth.socialaccount.providers.oauth2.client import OAuth2Client
    from allauth.socialaccount.models import SocialApp
    from django.contrib.sites.models import Site
    
    # Redirect to Google OAuth
    return redirect('/accounts/google/login/')

def google_login(request):
    """Redirect to Google OAuth login"""
    from django.shortcuts import redirect
    return redirect('/accounts/google/login/')
