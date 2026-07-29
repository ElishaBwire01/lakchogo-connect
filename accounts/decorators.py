from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth import get_user_model
from .models import UserRole

User = get_user_model()

def role_required(allowed_roles):
    """Decorator to restrict views to specific roles"""
    def decorator(view_func):
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                messages.error(request, 'Please login to access this page.')
                return redirect('accounts:login')
            
            # Superusers have access to everything
            if request.user.is_superuser:
                return view_func(request, *args, **kwargs)
            
            # Check if user has any of the allowed roles
            user_roles = UserRole.objects.filter(
                user=request.user,
                is_active=True
            ).values_list('role__name', flat=True)
            
            has_role = any(role in user_roles for role in allowed_roles)
            
            if not has_role:
                messages.error(request, 'You do not have permission to access this page.')
                return redirect('dashboard:index')
            
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator

def member_required(view_func):
    """Decorator to require member status"""
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, 'Please login to access this page.')
            return redirect('accounts:login')
        
        if not hasattr(request.user, 'member') or not request.user.member.is_active:
            messages.error(request, 'You must be a registered member to access this page.')
            return redirect('dashboard:index')
        
        return view_func(request, *args, **kwargs)
    return wrapper

def committee_member_required(view_func):
    """Decorator to require committee member status"""
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, 'Please login to access this page.')
            return redirect('accounts:login')
        
        if not request.user.is_committee and not request.user.is_superuser:
            messages.error(request, 'You must be a committee member to access this page.')
            return redirect('dashboard:index')
        
        return view_func(request, *args, **kwargs)
    return wrapper

def admin_required(view_func):
    """Decorator to require admin status"""
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, 'Please login to access this page.')
            return redirect('accounts:login')
        
        if not request.user.is_superuser and not request.user.is_staff:
            messages.error(request, 'You must be an admin to access this page.')
            return redirect('dashboard:index')
        
        return view_func(request, *args, **kwargs)
    return wrapper
