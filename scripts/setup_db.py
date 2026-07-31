#!/usr/bin/env python
"""
Database setup script for LakChogo Connect.
Run this script to initialize the database with default data.
"""

import os
import sys
import django

# Set up Django environment
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lakchogo.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.core.management import call_command
from accounts.models import Role
from members.models import Member
from finance.models import PaymentCategory
from compliance.models import ComplianceRule

User = get_user_model()

def setup_database():
    """Initialize database with default data"""
    print("=" * 60)
    print("LAKCHOGO CONNECT - DATABASE SETUP")
    print("=" * 60)
    
    # 1. Run migrations
    print("\n📦 Running migrations...")
    call_command('migrate', verbosity=0)
    print("✅ Migrations completed!")
    
    # 2. Create default roles
    print("\n👤 Creating default roles...")
    roles = [
        {'name': 'Admin', 'description': 'System administrator with full access', 'is_default': False},
        {'name': 'Treasurer', 'description': 'Handles all financial transactions', 'is_default': False},
        {'name': 'Secretary', 'description': 'Manages meetings and records', 'is_default': False},
        {'name': 'Welfare Officer', 'description': 'Manages welfare and bereavement events', 'is_default': False},
        {'name': 'Member', 'description': 'Regular group member', 'is_default': True},
    ]
    
    for role_data in roles:
        role, created = Role.objects.get_or_create(
            name=role_data['name'],
            defaults={
                'description': role_data['description'],
                'is_default': role_data['is_default']
            }
        )
        if created:
            print(f"  ✅ Created role: {role.name}")
        else:
            print(f"  ℹ️ Role already exists: {role.name}")
    
    # 3. Create default payment categories
    print("\n💰 Creating default payment categories...")
    categories = [
        {'name': 'Yearly Subscription', 'description': 'Annual membership fee', 'default_amount': 500, 'frequency': 'yearly', 'is_mandatory_for_welfare': True, 'icon': 'fa-calendar', 'color': 'primary'},
        {'name': 'Emergency Fund', 'description': 'Emergency contribution fund', 'default_amount': 200, 'frequency': 'monthly', 'is_mandatory_for_welfare': True, 'icon': 'fa-exclamation-triangle', 'color': 'danger'},
        {'name': 'Constitution Fee', 'description': 'One-time constitution fee', 'default_amount': 100, 'frequency': 'one-time', 'is_mandatory_for_welfare': True, 'icon': 'fa-gavel', 'color': 'warning'},
        {'name': 'Registration Fee', 'description': 'One-time registration fee', 'default_amount': 50, 'frequency': 'one-time', 'is_mandatory_for_welfare': False, 'icon': 'fa-user-plus', 'color': 'info'},
        {'name': 'Development Fund', 'description': 'Group development contributions', 'default_amount': 300, 'frequency': 'quarterly', 'is_mandatory_for_welfare': False, 'icon': 'fa-building', 'color': 'success'},
        {'name': 'Bereavement Fund', 'description': 'Bereavement support contributions', 'default_amount': 150, 'frequency': 'monthly', 'is_mandatory_for_welfare': True, 'icon': 'fa-heart', 'color': 'danger'},
        {'name': 'Other Collections', 'description': 'Other group collections', 'default_amount': 0, 'frequency': 'one-time', 'is_mandatory_for_welfare': False, 'icon': 'fa-money-bill', 'color': 'secondary'},
    ]
    
    for cat_data in categories:
        category, created = PaymentCategory.objects.get_or_create(
            name=cat_data['name'],
            defaults=cat_data
        )
        if created:
            print(f"  ✅ Created category: {category.name}")
        else:
            print(f"  ℹ️ Category already exists: {category.name}")
    
    # 4. Create default compliance rules
    print("\n📋 Creating default compliance rules...")
    rules = [
        {
            'name': 'Payment Compliance',
            'description': 'Members must make payments on time',
            'rule_type': 'payment',
            'grace_period_days': 30,
            'penalty_points': 10,
            'is_active': True,
            'order': 1
        },
        {
            'name': 'Attendance Compliance',
            'description': 'Members must attend at least 75% of meetings',
            'rule_type': 'attendance',
            'min_attendance_percentage': 75,
            'grace_period_days': 0,
            'penalty_points': 15,
            'is_active': True,
            'order': 2
        },
    ]
    
    for rule_data in rules:
        rule, created = ComplianceRule.objects.get_or_create(
            name=rule_data['name'],
            defaults=rule_data
        )
        if created:
            print(f"  ✅ Created rule: {rule.name}")
        else:
            print(f"  ℹ️ Rule already exists: {rule.name}")
    
    # 5. Create superuser if none exists
    print("\n👑 Checking for superuser...")
    if not User.objects.filter(is_superuser=True).exists():
        print("  ℹ️ No superuser found. Creating one...")
        username = input("  Enter superuser username (default: admin): ") or 'admin'
        email = input("  Enter email (default: admin@lakchogo.com): ") or 'admin@lakchogo.com'
        password = input("  Enter password (min 8 chars): ")
        
        if len(password) < 8:
            print("  ❌ Password must be at least 8 characters.")
            return
        
        User.objects.create_superuser(
            username=username,
            email=email,
            phone='+254700000000',
            id_number='00000000',
            password=password,
            first_name='Admin',
            last_name='User'
        )
        print(f"  ✅ Superuser '{username}' created!")
    else:
        admin = User.objects.filter(is_superuser=True).first()
        print(f"  ✅ Superuser exists: {admin.username}")
    
    # 6. Summary
    print("\n" + "=" * 60)
    print("✅ DATABASE SETUP COMPLETE!")
    print("=" * 60)
    print(f"\n📊 Summary:")
    print(f"  • Roles: {Role.objects.count()}")
    print(f"  • Payment Categories: {PaymentCategory.objects.count()}")
    print(f"  • Compliance Rules: {ComplianceRule.objects.count()}")
    print(f"  • Users: {User.objects.count()}")
    print(f"  • Members: {Member.objects.count()}")
    print("\n🚀 You can now run the server: python manage.py runserver")
    print("=" * 60)

if __name__ == '__main__':
    setup_database()
