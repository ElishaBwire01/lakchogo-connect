#!/usr/bin/env python
"""
Simple script to populate LakChogo Connect with sample data
Run this to make the system busy with users, members, payments, etc.
"""

import os
import sys
import django
import random
from datetime import datetime, timedelta
from django.utils import timezone

# Set up Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lakchogo.settings')
django.setup()

from django.contrib.auth import get_user_model
from members.models import Member, MemberContributionSummary
from finance.models import PaymentCategory, Payment
from meetings.models import Meeting, Attendance
from compliance.models import ComplianceScore
from welfare.models import BereavementEvent, BereavementContribution
from communications.models import ChatRoom, ChatMessage, Notification

User = get_user_model()

# Sample data
FIRST_NAMES = ['John', 'Mary', 'Peter', 'Jane', 'Michael', 'Sarah', 'David', 'Grace', 
               'James', 'Margaret', 'Paul', 'Catherine', 'Stephen', 'Alice', 'Joseph', 
               'Lucy', 'Samuel', 'Rose', 'Elias', 'Esther', 'Robert', 'Elizabeth', 
               'William', 'Helen', 'Thomas', 'Ann', 'Charles', 'Ruth', 'Daniel', 'Susan']

LAST_NAMES = ['Kamau', 'Ochieng', 'Muthoni', 'Ndegwa', 'Okoth', 'Wanjiru', 'Odhiambo', 
              'Akinyi', 'Omondi', 'Mwangi', 'Chebet', 'Kiprop', 'Kosgei', 'Cheruiyot', 
              'Kipchoge', 'Maritim', 'Kiptoo', 'Rotich', 'Kipngetich', 'Kiplagat']

PAYMENT_TYPES = [
    ('Yearly Subscription', 500, 'yearly', True),
    ('Emergency Fund', 200, 'monthly', True),
    ('Constitution Fee', 100, 'one-time', True),
    ('Registration Fee', 50, 'one-time', False),
    ('Development Fund', 300, 'quarterly', False),
    ('Bereavement Fund', 150, 'monthly', True),
]

def random_phone():
    return f"254{random.randint(700000000, 799999999)}"

def random_id():
    return ''.join([str(random.randint(0, 9)) for _ in range(8)])

def create_users_and_members(count=30):
    """Create users and members"""
    print(f"👤 Creating {count} users and members...")
    created = 0
    
    for i in range(count):
        first = random.choice(FIRST_NAMES)
        last = random.choice(LAST_NAMES)
        username = f"{first.lower()}.{last.lower()}{i+1}"
        phone = random_phone()
        
        if User.objects.filter(phone=phone).exists():
            continue
        
        user = User.objects.create_user(
            username=username,
            first_name=first,
            last_name=last,
            phone=phone,
            id_number=random_id(),
            email=f"{username}@lakchogo.com",
            password='Test123456'
        )
        
        member = Member.objects.create(
            user=user,
            status='active',
            next_of_kin_name=f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}",
            next_of_kin_phone=random_phone(),
            next_of_kin_relationship=random.choice(['Spouse', 'Sibling', 'Parent', 'Child']),
            gender=random.choice(['male', 'female']),
            occupation=random.choice(['Teacher', 'Doctor', 'Engineer', 'Business', 'Farmer', 'Student'])
        )
        
        # Use get_or_create to avoid duplicate error
        ComplianceScore.objects.get_or_create(
            member=member,
            defaults={
                'status': random.choice(['green', 'green', 'green', 'yellow', 'red']),
                'score': random.randint(60, 100)
            }
        )
        
        # Create contribution summary
        MemberContributionSummary.objects.get_or_create(member=member)
        
        created += 1
        if (i+1) % 10 == 0:
            print(f"  ✅ Created {created} members so far...")
    
    print(f"  ✅ Created {created} members total!")
    return created

def create_payment_categories():
    """Create payment categories"""
    print("💰 Creating payment categories...")
    for name, amount, freq, mandatory in PAYMENT_TYPES:
        cat, created = PaymentCategory.objects.get_or_create(
            name=name,
            defaults={
                'default_amount': amount,
                'frequency': freq,
                'is_mandatory_for_welfare': mandatory,
                'is_active': True,
                'icon': 'fa-money-bill',
                'color': random.choice(['primary', 'success', 'warning', 'danger', 'info'])
            }
        )
        if created:
            print(f"  ✅ Created: {name}")
    return PaymentCategory.objects.count()

def create_payments(count=100):
    """Create random payments"""
    print(f"💰 Creating {count} payments...")
    members = list(Member.objects.filter(status='active'))
    categories = list(PaymentCategory.objects.filter(is_active=True))
    
    if not members or not categories:
        print("  ❌ No members or categories found")
        return 0
    
    created = 0
    for _ in range(count):
        member = random.choice(members)
        category = random.choice(categories)
        amount = category.default_amount or random.randint(50, 500)
        
        Payment.objects.create(
            member=member,
            category=category,
            amount=amount,
            payment_method=random.choice(['mpesa', 'cash', 'airtel']),
            status=random.choice(['completed', 'completed', 'completed', 'pending']),
            notes=f"Payment for {category.name}"
        )
        created += 1
    
    print(f"  ✅ Created {created} payments")
    return created

def create_meetings(count=10):
    """Create meetings with attendance"""
    print(f"📅 Creating {count} meetings...")
    members = list(Member.objects.filter(status='active'))
    superuser = User.objects.filter(is_superuser=True).first()
    
    if not members:
        print("  ❌ No members found")
        return 0
    
    created = 0
    for i in range(count):
        meeting = Meeting.objects.create(
            title=f"Meeting #{i+1}: {random.choice(['Monthly', 'Quarterly', 'Emergency', 'Planning', 'Review'])}",
            date=timezone.now() + timedelta(days=random.randint(-30, 60)),
            venue=random.choice(['Conference Room A', 'Hall B', 'Online (Zoom)', 'Community Center', 'Church Hall']),
            agenda=f"Agenda items for meeting {i+1}...",
            status=random.choice(['scheduled', 'completed', 'completed', 'scheduled']),
            created_by=superuser or User.objects.first()
        )
        created += 1
        
        # Add attendance for some members
        for member in random.sample(members, min(random.randint(5, 20), len(members))):
            Attendance.objects.create(
                meeting=meeting,
                member=member,
                status=random.choice(['present', 'present', 'present', 'absent', 'excused'])
            )
    
    print(f"  ✅ Created {created} meetings with attendance")
    return created

def create_welfare_events(count=5):
    """Create welfare events"""
    print(f"❤️ Creating {count} welfare events...")
    members = list(Member.objects.filter(status='active'))
    
    if not members:
        print("  ❌ No members found")
        return 0
    
    created = 0
    for _ in range(count):
        member = random.choice(members)
        target = random.randint(20000, 100000)
        
        event = BereavementEvent.objects.create(
            member=member,
            deceased_name=f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}",
            relationship=random.choice(['Father', 'Mother', 'Spouse', 'Child', 'Sibling']),
            date_of_death=timezone.now().date() - timedelta(days=random.randint(1, 30)),
            collection_target=target,
            status=random.choice(['active', 'active', 'closed'])
        )
        created += 1
        
        # Add contributions
        for _ in range(random.randint(5, 20)):
            contributor = random.choice(members)
            amount = random.randint(100, 5000)
            BereavementContribution.objects.create(
                event=event,
                contributor=contributor,
                amount=amount,
                contributor_name=contributor.get_full_name(),
                payment_method=random.choice(['mpesa', 'cash'])
            )
            event.amount_collected += amount
            event.save()
    
    print(f"  ✅ Created {created} welfare events")
    return created

def create_chat_rooms(count=3):
    """Create chat rooms with messages"""
    print(f"💬 Creating {count} chat rooms...")
    members = list(User.objects.filter(is_active=True))[:30]
    
    if len(members) < 2:
        print("  ❌ Not enough users")
        return 0
    
    created = 0
    for _ in range(count):
        # Create room with random members
        room = ChatRoom.objects.create(
            name=f"Chat Room {_+1}",
            room_type=random.choice(['group', 'group', 'committee']),
            created_by=random.choice(members)
        )
        room.members.add(*random.sample(members, min(random.randint(3, 10), len(members))))
        created += 1
        
        # Add messages
        for _ in range(random.randint(5, 20)):
            sender = random.choice(room.members.all())
            ChatMessage.objects.create(
                room=room,
                sender=sender,
                message_type='text',
                content=random.choice([
                    "Hello everyone!",
                    "How is everyone doing?",
                    "When is the next meeting?",
                    "I have a question about the payments.",
                    "Thanks for the update!",
                    "Can we schedule a meeting?",
                    "I'll be attending the next event.",
                    "Great work everyone!",
                    "Please check the latest announcements.",
                    "I need help with something.",
                    "The system is working great!",
                    "When are the reports due?",
                    "I've made my payment.",
                    "Let's organize a team meeting.",
                    "Thanks for the information.",
                ])
            )
    
    print(f"  ✅ Created {created} chat rooms with messages")
    return created

def create_notifications(count=50):
    """Create notifications"""
    print(f"🔔 Creating {count} notifications...")
    users = list(User.objects.filter(is_active=True))
    
    if not users:
        print("  ❌ No users found")
        return 0
    
    created = 0
    types = ['system', 'announcement', 'payment_reminder', 'meeting_reminder', 'welfare_alert', 'compliance_alert']
    titles = [
        "Welcome to LakChogo Connect!",
        "New Announcement",
        "Payment Reminder",
        "Meeting Reminder",
        "Welfare Event Update",
        "Compliance Alert",
        "System Update",
        "New Member Joined",
        "Report Ready",
        "Meeting Scheduled"
    ]
    messages = [
        "This is a system notification.",
        "Please check the latest announcements.",
        "Your payment is due soon.",
        "Don't forget the meeting tomorrow.",
        "A new welfare event has been created.",
        "Your compliance status needs attention.",
        "The system has been updated.",
        "Welcome to the group!",
        "Your report is ready for download.",
        "A new meeting has been scheduled."
    ]
    
    for _ in range(count):
        user = random.choice(users)
        Notification.objects.create(
            recipient=user,
            notification_type=random.choice(types),
            title=random.choice(titles),
            message=random.choice(messages),
            channel='in_app',
            status=random.choice(['sent', 'read']),
            priority='normal'
        )
        created += 1
    
    print(f"  ✅ Created {created} notifications")
    return created

def main():
    """Run all population functions"""
    print("=" * 60)
    print("🚀 LAKCHOGO CONNECT - DATA POPULATOR")
    print("=" * 60)
    
    # Check if data already exists
    if Member.objects.count() > 0:
        confirm = input(f"\n⚠️ {Member.objects.count()} members already exist. Add more? (y/n): ")
        if confirm.lower() != 'y':
            print("❌ Cancelled.")
            return
    
    # Populate data
    print("\n📊 Creating data...\n")
    
    members = create_users_and_members(30)
    categories = create_payment_categories()
    payments = create_payments(100)
    meetings = create_meetings(10)
    welfare = create_welfare_events(5)
    chat = create_chat_rooms(3)
    notifications = create_notifications(50)
    
    # Summary
    print("\n" + "=" * 60)
    print("✅ POPULATION COMPLETE!")
    print("=" * 60)
    print(f"\n📊 Summary:")
    print(f"  • Members: {Member.objects.count()}")
    print(f"  • Payment Categories: {PaymentCategory.objects.count()}")
    print(f"  • Payments: {Payment.objects.count()}")
    print(f"  • Meetings: {Meeting.objects.count()}")
    print(f"  • Attendances: {Attendance.objects.count()}")
    print(f"  • Welfare Events: {BereavementEvent.objects.count()}")
    print(f"  • Welfare Contributions: {BereavementContribution.objects.count()}")
    print(f"  • Chat Rooms: {ChatRoom.objects.count()}")
    print(f"  • Chat Messages: {ChatMessage.objects.count()}")
    print(f"  • Notifications: {Notification.objects.count()}")
    print(f"  • Users: {User.objects.count()}")
    print("\n🔑 Test Credentials:")
    print("  • Username: Any seeded user (e.g., john.kamau1)")
    print("  • Password: Test123456")
    print("=" * 60)

if __name__ == '__main__':
    main()
