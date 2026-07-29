from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Role, UserRole, UserActivityLog

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'get_full_name', 'phone', 'email', 'is_active', 'is_staff', 'date_joined')
    list_filter = ('is_active', 'is_staff', 'is_superuser', 'date_joined')
    search_fields = ('username', 'first_name', 'last_name', 'phone', 'email', 'id_number')
    ordering = ('-date_joined',)
    
    fieldsets = UserAdmin.fieldsets + (
        ('Additional Info', {
            'fields': ('phone', 'id_number', 'profile_picture', 'is_committee')
        }),
    )
    
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Additional Info', {
            'fields': ('phone', 'id_number', 'first_name', 'last_name')
        }),
    )

@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'is_default', 'created_at')
    list_filter = ('is_default', 'created_at')
    search_fields = ('name', 'description')
    filter_horizontal = ('permissions',)

@admin.register(UserRole)
class UserRoleAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'assigned_by', 'assigned_at', 'is_active')
    list_filter = ('is_active', 'assigned_at')
    search_fields = ('user__username', 'role__name')
    raw_id_fields = ('user', 'role', 'assigned_by')

@admin.register(UserActivityLog)
class UserActivityLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'action', 'description', 'timestamp', 'ip_address')
    list_filter = ('action', 'timestamp')
    search_fields = ('user__username', 'description')
    raw_id_fields = ('user',)
    date_hierarchy = 'timestamp'
