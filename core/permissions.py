"""
Custom permission classes for LakChogo Connect
Used for role-based access control
"""

from rest_framework import permissions
from accounts.models import UserRole

class IsAdmin(permissions.BasePermission):
    """Permission: User must be an Admin"""
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        if request.user.is_superuser:
            return True
        
        return UserRole.objects.filter(
            user=request.user,
            role__name='Admin',
            is_active=True
        ).exists()


class IsTreasurer(permissions.BasePermission):
    """Permission: User must be a Treasurer"""
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        if request.user.is_superuser:
            return True
        
        return UserRole.objects.filter(
            user=request.user,
            role__name__in=['Treasurer', 'Admin'],
            is_active=True
        ).exists()


class IsSecretary(permissions.BasePermission):
    """Permission: User must be a Secretary"""
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        if request.user.is_superuser:
            return True
        
        return UserRole.objects.filter(
            user=request.user,
            role__name__in=['Secretary', 'Admin'],
            is_active=True
        ).exists()


class IsWelfareOfficer(permissions.BasePermission):
    """Permission: User must be a Welfare Officer"""
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        if request.user.is_superuser:
            return True
        
        return UserRole.objects.filter(
            user=request.user,
            role__name__in=['Welfare Officer', 'Admin'],
            is_active=True
        ).exists()


class IsCommitteeMember(permissions.BasePermission):
    """Permission: User must be a Committee Member"""
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        if request.user.is_superuser:
            return True
        
        return UserRole.objects.filter(
            user=request.user,
            role__name__in=['Admin', 'Treasurer', 'Secretary', 'Welfare Officer'],
            is_active=True
        ).exists()


class IsMember(permissions.BasePermission):
    """Permission: User must be a registered Member"""
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        if request.user.is_superuser:
            return True
        
        return hasattr(request.user, 'member') and request.user.member.is_active


class IsOwner(permissions.BasePermission):
    """Permission: User must be the owner of the object"""
    
    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            return False
        
        if request.user.is_superuser:
            return True
        
        # Check if user is the owner (has user field)
        if hasattr(obj, 'user'):
            return obj.user == request.user
        
        # Check if user is the creator
        if hasattr(obj, 'created_by'):
            return obj.created_by == request.user
        
        return False
