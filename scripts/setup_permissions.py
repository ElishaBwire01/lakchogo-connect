#!/usr/bin/env python
import os
import sys
import django

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lakchogo.settings')
django.setup()

from accounts.permissions import create_permissions
from accounts.models import Role
from django.contrib.auth import get_user_model

User = get_user_model()

def setup_permissions():
    print("=" * 60)
    print("Setting up permissions and roles...")
    print("=" * 60)
    
    # Create permissions
    permissions = create_permissions()
    print(f"\n✅ Created {len(permissions)} permissions")
    
    # Define roles with permissions
    roles_data = {
        'Admin': {
            'description': 'Full system access with all permissions',
            'permissions': list(permissions.keys())
        },
        'Treasurer': {
            'description': 'Manage financial transactions and payments',
            'permissions': [
                'can_record_payment', 'can_approve_payment', 'can_view_payments',
                'can_manage_categories', 'can_export_finance', 'can_view_dashboard',
                'can_view_members', 'can_generate_reports', 'can_export_reports'
            ]
        },
        'Secretary': {
            'description': 'Manage meetings, minutes, and attendance',
            'permissions': [
                'can_create_meeting', 'can_edit_meeting', 'can_view_meetings',
                'can_take_attendance', 'can_manage_minutes', 'can_view_dashboard',
                'can_view_members', 'can_send_announcements', 'can_view_compliance'
            ]
        },
        'Welfare Officer': {
            'description': 'Manage welfare and bereavement events',
            'permissions': [
                'can_create_welfare', 'can_edit_welfare', 'can_view_welfare',
                'can_disburse_funds', 'can_approve_welfare', 'can_view_dashboard',
                'can_view_members', 'can_view_compliance'
            ]
        },
        'Member': {
            'description': 'Basic member access',
            'permissions': [
                'can_view_members', 'can_view_meetings', 'can_view_payments',
                'can_view_welfare', 'can_view_compliance', 'can_view_dashboard',
                'can_view_chat'
            ]
        }
    }
    
    # Create or update roles
    print("\n📋 Setting up roles...")
    for role_name, role_data in roles_data.items():
        role, created = Role.objects.get_or_create(
            name=role_name,
            defaults={'description': role_data['description']}
        )
        
        if created:
            print(f"  ✅ Created role: {role_name}")
        else:
            print(f"  🔄 Updated role: {role_name}")
            role.description = role_data['description']
            role.save()
        
        # Add permissions
        role.permissions.clear()
        for perm_codename in role_data['permissions']:
            if perm_codename in permissions:
                role.permissions.add(permissions[perm_codename])
        
        print(f"  📋 Added {role.permissions.count()} permissions to {role_name}")
    
    # Set Member as default role
    member_role = Role.objects.get(name='Member')
    member_role.is_default = True
    member_role.save()
    print(f"\n✅ Set '{member_role.name}' as default role")
    
    # Summary
    print("\n" + "=" * 60)
    print("✅ SETUP COMPLETE!")
    print("=" * 60)
    print(f"\n📊 Summary:")
    print(f"  • Roles: {Role.objects.count()}")
    print(f"  • Permissions: {len(permissions)}")
    print(f"  • Default Role: Member")
    print("\n🚀 You can now assign roles to users via the admin panel")
    print("=" * 60)

if __name__ == '__main__':
    setup_permissions()
