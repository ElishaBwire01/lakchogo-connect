#!/usr/bin/env python
"""
Test script for LakChogo Connect Notifications
Run this script to trigger various notifications and test the system
"""

import os
import sys
import django
import random
from datetime import datetime, timedelta

# Set up Django environment
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lakchogo.settings')
django.setup()

from django.contrib.auth import get_user_model
from communications.models import Notification
from communications.services import NotificationService, NotificationTriggers
from members.models import Member
from finance.models import Payment, PaymentCategory
from meetings.models import Meeting

User = get_user_model()

def get_or_create_user():
    """Get the superuser or create a test user"""
    user = User.objects.filter(is_superuser=True).first()
    if not user:
        user = User.objects.filter(is_active=True).first()
    if not user:
        # Create a test user
        user = User.objects.create_user(
            username='testuser',
            phone='+254712345678',
            password='Test123456',
            first_name='Test',
            last_name='User',
            id_number='12345678',
            email='test@lakchogo.com'
        )
        print(f"✅ Created test user: {user.username}")
    return user

def test_single_notification():
    """Test sending a single notification"""
    print("\n📨 Testing Single Notification...")
    user = get_or_create_user()
    
    notification = Notification.create_notification(
        recipient=user,
        notification_type='system',
        title='🧪 Test Notification',
        message='This is a test notification to verify the system is working!',
        action_url='/dashboard/',
        priority='high'
    )
    
    print(f"✅ Notification created: {notification.title}")
    print(f"   ID: {notification.id}")
    print(f"   Status: {notification.status}")
    print(f"   To: {user.get_full_name()}")
    return notification

def test_bulk_notifications():
    """Test sending bulk notifications"""
    print("\n📨 Testing Bulk Notifications...")
    users = User.objects.filter(is_active=True)[:5]
    
    if not users:
        print("❌ No active users found")
        return
    
    notifications = Notification.create_bulk_notifications(
        recipients=users,
        notification_type='system',
        title='📢 System Test Notification',
        message='This is a bulk test notification sent to multiple users!',
        action_url='/dashboard/',
        priority='normal'
    )
    
    print(f"✅ Created {len(notifications)} bulk notifications")
    return notifications

def test_payment_notification():
    """Test payment notification triggers"""
    print("\n💰 Testing Payment Notification...")
    user = get_or_create_user()
    
    # Get or create member
    member = Member.objects.filter(user=user).first()
    if not member:
        member = Member.objects.create(user=user, status='active')
    
    # Get or create payment category
    category = PaymentCategory.objects.filter(is_active=True).first()
    if not category:
        category = PaymentCategory.objects.create(
            name='Test Category',
            default_amount=100,
            is_active=True
        )
    
    # Create test payment
    payment = Payment.objects.create(
        member=member,
        category=category,
        amount=100,
        payment_method='cash',
        status='completed',
        recorded_by=user,
        notes='Test payment for notification'
    )
    
    # Trigger payment notification
    NotificationTriggers.payment_created(payment)
    print(f"✅ Payment notification triggered for: {member.get_full_name()}")
    return payment

def test_meeting_notification():
    """Test meeting notification triggers"""
    print("\n📅 Testing Meeting Notification...")
    user = get_or_create_user()
    
    # Create test meeting
    meeting = Meeting.objects.create(
        title='Test Meeting for Notifications',
        date=datetime.now() + timedelta(days=3),
        venue='Test Venue',
        created_by=user,
        status='scheduled'
    )
    
    # Trigger meeting notification
    NotificationTriggers.meeting_scheduled(meeting)
    print(f"✅ Meeting notification triggered: {meeting.title}")
    return meeting

def test_compliance_notification():
    """Test compliance notification triggers"""
    print("\n📋 Testing Compliance Notification...")
    user = get_or_create_user()
    
    # Get or create member
    member = Member.objects.filter(user=user).first()
    if not member:
        member = Member.objects.create(user=user, status='active')
    
    # Get or create compliance score
    from compliance.models import ComplianceScore
    score, created = ComplianceScore.objects.get_or_create(
        member=member,
        defaults={
            'status': 'yellow',
            'score': 65,
            'payment_compliance': 70,
            'attendance_compliance': 60
        }
    )
    
    if not created:
        score.status = 'yellow'
        score.score = 65
        score.save()
    
    # Trigger compliance notification
    NotificationTriggers.compliance_updated(score)
    print(f"✅ Compliance notification triggered for: {member.get_full_name()}")
    return score

def test_welfare_notification():
    """Test welfare notification triggers"""
    print("\n❤️ Testing Welfare Notification...")
    user = get_or_create_user()
    
    # Get or create member
    member = Member.objects.filter(user=user).first()
    if not member:
        member = Member.objects.create(user=user, status='active')
    
    # Create test welfare event
    from welfare.models import BereavementEvent
    event = BereavementEvent.objects.create(
        member=member,
        deceased_name='Test Deceased',
        relationship='Test Relationship',
        date_of_death=datetime.now().date(),
        collection_target=10000,
        status='active'
    )
    
    # Trigger welfare notification
    NotificationTriggers.welfare_event_created(event)
    print(f"✅ Welfare notification triggered for: {event.deceased_name}")
    return event

def view_all_notifications():
    """View all existing notifications"""
    print("\n📋 Viewing All Notifications...")
    notifications = Notification.objects.all().order_by('-created_at')
    
    if not notifications:
        print("❌ No notifications found")
        return
    
    print(f"📊 Total Notifications: {notifications.count()}")
    print("-" * 60)
    
    for i, notification in enumerate(notifications[:20], 1):
        status_icon = "🟢" if notification.status == 'read' else "🔵"
        print(f"{i}. {status_icon} {notification.title}")
        print(f"   To: {notification.recipient.get_full_name() if notification.recipient else 'No recipient'}")
        print(f"   Type: {notification.get_notification_type_display()}")
        print(f"   Status: {notification.status}")
        print(f"   Created: {notification.created_at.strftime('%Y-%m-%d %H:%M')}")
        print(f"   Message: {notification.message[:100]}...")
        print("-" * 40)

def clear_notifications():
    """Delete all notifications"""
    print("\n🗑️ Clearing Notifications...")
    confirm = input("Are you sure you want to delete ALL notifications? (y/n): ")
    if confirm.lower() == 'y':
        count = Notification.objects.count()
        Notification.objects.all().delete()
        print(f"✅ Deleted {count} notifications")
    else:
        print("❌ Cancelled")

def show_help():
    """Show available commands"""
    print("""
============================================================
LAKCHOGO CONNECT - NOTIFICATION TEST SCRIPT
============================================================

Commands:
  python scripts/test_notifications.py all          - Run all tests
  python scripts/test_notifications.py single       - Test single notification
  python scripts/test_notifications.py bulk         - Test bulk notifications
  python scripts/test_notifications.py payment      - Test payment notification
  python scripts/test_notifications.py meeting      - Test meeting notification
  python scripts/test_notifications.py compliance   - Test compliance notification
  python scripts/test_notifications.py welfare      - Test welfare notification
  python scripts/test_notifications.py view         - View all notifications
  python scripts/test_notifications.py clear        - Clear all notifications
  python scripts/test_notifications.py help         - Show this help

Examples:
  # Run all tests
  python scripts/test_notifications.py all
  
  # View existing notifications
  python scripts/test_notifications.py view
============================================================
""")

def run_all_tests():
    """Run all notification tests"""
    print("=" * 60)
    print("🚀 RUNNING ALL NOTIFICATION TESTS")
    print("=" * 60)
    
    test_single_notification()
    test_bulk_notifications()
    test_payment_notification()
    test_meeting_notification()
    test_compliance_notification()
    test_welfare_notification()
    
    print("\n" + "=" * 60)
    print("✅ ALL TESTS COMPLETE!")
    view_all_notifications()
    print("=" * 60)

if __name__ == '__main__':
    args = sys.argv[1:] if len(sys.argv) > 1 else ['help']
    command = args[0] if args else 'help'
    
    if command == 'all':
        run_all_tests()
    elif command == 'single':
        test_single_notification()
    elif command == 'bulk':
        test_bulk_notifications()
    elif command == 'payment':
        test_payment_notification()
    elif command == 'meeting':
        test_meeting_notification()
    elif command == 'compliance':
        test_compliance_notification()
    elif command == 'welfare':
        test_welfare_notification()
    elif command == 'view':
        view_all_notifications()
    elif command == 'clear':
        clear_notifications()
    else:
        show_help()
