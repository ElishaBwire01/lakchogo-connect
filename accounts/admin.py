from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Role, UserRole, UserActivityLog

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'get_full_name', 'phone', 'email', 'is_active', 'is_staff')
    list_filter = ('is_active', 'is_staff', 'is_superuser')
    search_fields = ('username', 'first_name', 'last_name', 'phone', 'email', 'id_number')
    ordering = ('-date_joined',)
    
    fieldsets = UserAdmin.fieldsets + (
        ('Additional Info', {
            'fields': ('phone', 'id_number', 'profile_picture', 'is_committee')
        }),
    )

@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'is_default', 'created_at')
    list_filter = ('is_default',)
    search_fields = ('name', 'description')

@admin.register(UserRole)
class UserRoleAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'assigned_by', 'assigned_at', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('user__username', 'role__name')

@admin.register(UserActivityLog)
class UserActivityLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'action', 'description', 'timestamp')
    list_filter = ('action', 'timestamp')
    search_fields = ('user__username', 'description')
