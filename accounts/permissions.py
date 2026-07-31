from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from .models import Role, UserRole

def create_permissions():
    """Create custom permissions for the system"""
    
    # Get content types for all apps
    apps = ['accounts', 'members', 'finance', 'meetings', 'compliance', 'welfare', 'communications', 'reports', 'dashboard']
    
    permissions = {
        # Accounts permissions
        'can_manage_users': ('accounts', 'Can manage users'),
        'can_manage_roles': ('accounts', 'Can manage roles'),
        'can_view_audit_logs': ('accounts', 'Can view audit logs'),
        
        # Members permissions
        'can_add_member': ('members', 'Can add members'),
        'can_edit_member': ('members', 'Can edit members'),
        'can_delete_member': ('members', 'Can delete members'),
        'can_view_members': ('members', 'Can view members'),
        'can_approve_members': ('members', 'Can approve members'),
        
        # Finance permissions
        'can_record_payment': ('finance', 'Can record payments'),
        'can_approve_payment': ('finance', 'Can approve payments'),
        'can_delete_payment': ('finance', 'Can delete payments'),
        'can_view_payments': ('finance', 'Can view payments'),
        'can_manage_categories': ('finance', 'Can manage payment categories'),
        'can_export_finance': ('finance', 'Can export financial reports'),
        
        # Meetings permissions
        'can_create_meeting': ('meetings', 'Can create meetings'),
        'can_edit_meeting': ('meetings', 'Can edit meetings'),
        'can_delete_meeting': ('meetings', 'Can delete meetings'),
        'can_view_meetings': ('meetings', 'Can view meetings'),
        'can_take_attendance': ('meetings', 'Can take attendance'),
        'can_manage_minutes': ('meetings', 'Can manage meeting minutes'),
        
        # Compliance permissions
        'can_view_compliance': ('compliance', 'Can view compliance'),
        'can_manage_rules': ('compliance', 'Can manage compliance rules'),
        'can_run_checks': ('compliance', 'Can run compliance checks'),
        'can_resolve_alerts': ('compliance', 'Can resolve compliance alerts'),
        
        # Welfare permissions
        'can_create_welfare': ('welfare', 'Can create welfare events'),
        'can_edit_welfare': ('welfare', 'Can edit welfare events'),
        'can_delete_welfare': ('welfare', 'Can delete welfare events'),
        'can_view_welfare': ('welfare', 'Can view welfare events'),
        'can_disburse_funds': ('welfare', 'Can disburse welfare funds'),
        'can_approve_welfare': ('welfare', 'Can approve welfare requests'),
        
        # Communications permissions
        'can_send_announcements': ('communications', 'Can send announcements'),
        'can_manage_notifications': ('communications', 'Can manage notifications'),
        'can_delete_messages': ('communications', 'Can delete chat messages'),
        'can_view_chat': ('communications', 'Can view chat'),
        
        # Reports permissions
        'can_generate_reports': ('reports', 'Can generate reports'),
        'can_delete_reports': ('reports', 'Can delete reports'),
        'can_export_reports': ('reports', 'Can export reports'),
        
        # Dashboard permissions
        'can_view_dashboard': ('dashboard', 'Can view dashboard'),
        'can_manage_widgets': ('dashboard', 'Can manage dashboard widgets'),
    }
    
    created_permissions = {}
    
    for codename, (app_label, name) in permissions.items():
        try:
            # Use get_or_create to handle multiple content types
            content_type, created = ContentType.objects.get_or_create(
                app_label=app_label,
                model='permission'  # Use a dummy model name
            )
            if created:
                # If we had to create it, we need to set the model properly
                pass
            
            permission, created = Permission.objects.get_or_create(
                codename=codename,
                content_type=content_type,
                defaults={'name': name}
            )
            created_permissions[codename] = permission
        except ContentType.DoesNotExist:
            print(f"Content type for {app_label} not found")
        except ContentType.MultipleObjectsReturned:
            # If multiple content types exist, use the first one
            content_type = ContentType.objects.filter(app_label=app_label).first()
            if content_type:
                permission, created = Permission.objects.get_or_create(
                    codename=codename,
                    content_type=content_type,
                    defaults={'name': name}
                )
                created_permissions[codename] = permission
    
    return created_permissions


def get_user_permissions(user):
    """Get all permissions for a user"""
    if user.is_superuser:
        return Permission.objects.all()
    
    # Get permissions from roles
    user_roles = UserRole.objects.filter(user=user, is_active=True)
    permissions = Permission.objects.none()
    
    for user_role in user_roles:
        permissions = permissions | user_role.role.permissions.all()
    
    return permissions


def user_has_permission(user, permission_codename):
    """Check if user has a specific permission"""
    if user.is_superuser:
        return True
    
    return get_user_permissions(user).filter(codename=permission_codename).exists()


def user_has_any_permission(user, permission_codenames):
    """Check if user has any of the listed permissions"""
    if user.is_superuser:
        return True
    
    return get_user_permissions(user).filter(codename__in=permission_codenames).exists()


def user_has_all_permissions(user, permission_codenames):
    """Check if user has all listed permissions"""
    if user.is_superuser:
        return True
    
    user_perms = get_user_permissions(user).filter(codename__in=permission_codenames)
    return user_perms.count() == len(permission_codenames)
