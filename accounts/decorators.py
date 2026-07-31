from django.shortcuts import redirect
from django.contrib import messages
from functools import wraps
from django.http import JsonResponse
from django.core.exceptions import PermissionDenied

def permission_required(permission_codename):
    """Decorator to check if user has a specific permission"""
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                messages.error(request, 'Please login to access this page.')
                return redirect('accounts:login')
            
            if request.user.has_permission(permission_codename):
                return view_func(request, *args, **kwargs)
            
            messages.error(request, 'You do not have permission to access this page.')
            return redirect('dashboard:index')
        return wrapper
    return decorator


def admin_required(view_func):
    """Decorator to check if user is admin"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, 'Please login to access this page.')
            return redirect('accounts:login')
        
        if request.user.is_admin or request.user.is_superuser:
            return view_func(request, *args, **kwargs)
        
        messages.error(request, 'Admin access required.')
        return redirect('dashboard:index')
    return wrapper


def committee_required(view_func):
    """Decorator to check if user is committee member"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, 'Please login to access this page.')
            return redirect('accounts:login')
        
        if request.user.is_committee_member or request.user.is_superuser:
            return view_func(request, *args, **kwargs)
        
        messages.error(request, 'Committee access required.')
        return redirect('dashboard:index')
    return wrapper


def treasurer_required(view_func):
    """Decorator to check if user is treasurer"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, 'Please login to access this page.')
            return redirect('accounts:login')
        
        if request.user.is_treasurer or request.user.is_superuser:
            return view_func(request, *args, **kwargs)
        
        messages.error(request, 'Treasurer access required.')
        return redirect('dashboard:index')
    return wrapper


def secretary_required(view_func):
    """Decorator to check if user is secretary"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, 'Please login to access this page.')
            return redirect('accounts:login')
        
        if request.user.is_secretary or request.user.is_superuser:
            return view_func(request, *args, **kwargs)
        
        messages.error(request, 'Secretary access required.')
        return redirect('dashboard:index')
    return wrapper


def welfare_officer_required(view_func):
    """Decorator to check if user is welfare officer"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, 'Please login to access this page.')
            return redirect('accounts:login')
        
        if request.user.is_welfare_officer or request.user.is_superuser:
            return view_func(request, *args, **kwargs)
        
        messages.error(request, 'Welfare Officer access required.')
        return redirect('dashboard:index')
    return wrapper


def member_required(view_func):
    """Decorator to check if user is a registered member"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, 'Please login to access this page.')
            return redirect('accounts:login')
        
        if request.user.is_member or request.user.is_superuser:
            return view_func(request, *args, **kwargs)
        
        messages.error(request, 'Member access required.')
        return redirect('dashboard:index')
    return wrapper
