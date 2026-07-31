from django.core.management.base import BaseCommand
from django.contrib.auth.models import Permission
from accounts.permissions import create_permissions
from accounts.models import Role

class Command(BaseCommand):
    help = 'Setup permissions and roles for the system'

    def handle(self, *args, **options):
        self.stdout.write('Setting up permissions...')
        
        # Create permissions
        permissions = create_permissions()
        self.stdout.write(f'Created {len(permissions)} permissions')
        
        # Create roles
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
        for role_name, role_data in roles_data.items():
            role, created = Role.objects.get_or_create(
                name=role_name,
                defaults={'description': role_data['description']}
            )
            
            if created:
                self.stdout.write(f'Created role: {role_name}')
            else:
                self.stdout.write(f'Updating role: {role_name}')
                role.description = role_data['description']
                role.save()
            
            # Add permissions to role
            role.permissions.clear()
            for perm_codename in role_data['permissions']:
                if perm_codename in permissions:
                    role.permissions.add(permissions[perm_codename])
            
            self.stdout.write(f'  Added {role.permissions.count()} permissions to {role_name}')
        
        self.stdout.write(self.style.SUCCESS('Permissions setup complete!'))
