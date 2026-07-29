from rest_framework import permissions
from .models import UserRole

class IsAdminUser(permissions.BasePermission):
    """Permission to check if user is admin"""
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        return UserRole.objects.filter(
            user=request.user,
            role__name__iexact='Admin',
            is_active=True
        ).exists() or request.user.is_superuser

class IsTreasurerUser(permissions.BasePermission):
    """Permission to check if user is treasurer"""
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        return UserRole.objects.filter(
            user=request.user,
            role__name__in=['Treasurer', 'Admin'],
            is_active=True
        ).exists() or request.user.is_superuser

class IsSecretaryUser(permissions.BasePermission):
    """Permission to check if user is secretary"""
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        return UserRole.objects.filter(
            user=request.user,
            role__name__in=['Secretary', 'Admin'],
            is_active=True
        ).exists() or request.user.is_superuser

class IsWelfareOfficer(permissions.BasePermission):
    """Permission to check if user is welfare officer"""
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        return UserRole.objects.filter(
            user=request.user,
            role__name__in=['Welfare Officer', 'Admin'],
            is_active=True
        ).exists() or request.user.is_superuser

class IsCommitteeMember(permissions.BasePermission):
    """Permission to check if user is committee member"""
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        return UserRole.objects.filter(
            user=request.user,
            role__name__in=['Admin', 'Treasurer', 'Secretary', 'Welfare Officer'],
            is_active=True
        ).exists() or request.user.is_superuser
