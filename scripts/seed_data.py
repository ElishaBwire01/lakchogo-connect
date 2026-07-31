#!/usr/bin/env python
"""
Data seeder script for LakChogo Connect.
Run this script to populate the database with sample/test data.
"""

import os
import sys
import django
from datetime import datetime, timedelta
from django.utils import timezone
import random

# Set up Django environment
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lakchogo.settings')
django.setup()

from django.contrib.auth import get_user_model
from accounts.models import Role
from members.models import Member, MemberContributionSummary
from finance.models import PaymentCategory, Payment
from meetings.models import Meeting, Attendance
from compliance.models import ComplianceScore

User = get_user_model()

# Sample data
FIRST_NAMES = ['John', 'Mary', 'Peter', 'Jane', 'Michael', 'Sarah', 'David', 'Grace', 'James', 'Margaret',
               'Paul', 'Catherine', 'Stephen', 'Alice', 'Joseph', 'Lucy', 'Samuel', 'Rose', 'Elias', 'Esther']
LAST_NAMES = ['Kamau', 'Ochieng', 'Muthoni', 'Ndegwa', 'Okoth', 'Wanjiru', 'Odhiambo', 'Akinyi', 'Omondi', 'Mwangi',
              'Chebet', 'Kiprop', 'Kosgei', 'Cheruiyot', 'Kipchoge', 'Maritim', 'Kiptoo', 'Rotich', 'Kipngetich', 'Kiplagat']

def generate_phone():
    """Generate a random Kenyan phone number"""
    prefixes = ['2547', '2541', '07', '01']
    prefix = random.choice(prefixes)
    number = ''.join([str(random.randint(0, 9)) for _ in range(8)])
    return prefix + number

def generate_id():
    """Generate a random ID number"""
    return ''.join([str(random.randint(0, 9)) for _ in range(8)])

def seed_members(count=20):
    """Seed members"""
    print(f"👤 Seeding {count} members...")
    created = 0
    
    for i in range(count):
        first_name = random.choice(FIRST_NAMES)
        last_name = random.choice(LAST_NAMES)
        username = f"{first_name.lower()}.{last_name.lower()}{i+1}"
        phone = generate_phone()
        
        if User.objects.filter(phone=phone).exists():
            continue
        
        user = User.objects.create_user(
            username=username,
            first_name=first_name,
            last_name=last_name,
            phone=phone,
            id_number=generate_id(),
            email=f"{username}@lakchogo.com",
            password='Test123456'
        )
        
        member = Member.objects.create(
            user=user,
            status='active',
            next_of_kin_name=f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}",
            next_of_kin_phone=generate_phone(),
            next_of_kin_relationship=random.choice(['Spouse', 'Sibling', 'Parent', 'Child']),
            gender=random.choice(['male', 'female']),
            occupation=random.choice(['Teacher', 'Doctor', 'Engineer', 'Business', 'Farmer', 'Student'])
        )
        
        # Create contribution summary
        MemberContributionSummary.objects.get_or_create(member=member)
        
        # Create compliance score
        ComplianceScore.objects.get_or_create(
            member=member,
            defaults={
                'status': random.choice(['green', 'yellow', 'red']),
                'score': random.randint(60, 100)
            }
        )
        
        created += 1
        if (i+1) % 5 == 0:
            print(f"  ✅ Created {created} members so far...")
    
    print(f"  ✅ Created {created} members total!")
    return created

def seed_payments(member_count=20):
    """Seed payments for members"""
    print(f"\n💰 Seeding payments...")
    created = 0
    categories = PaymentCategory.objects.filter(is_active=True)
    
    members = Member.objects.filter(status='active')[:member_count]
    
    for member in members:
        num_payments = random.randint(2, 5)
        for _ in range(num_payments):
            category = random.choice(categories)
            amount = category.default_amount * random.randint(1, 3)
            
            payment = Payment.objects.create(
                member=member,
                category=category,
                amount=amount if amount > 0 else 100,
                payment_method=random.choice(['cash', 'mpesa', 'airtel']),
                status=random.choice(['completed', 'completed', 'completed', 'pending']),
                notes=f"Payment for {category.name}",
                recorded_by=User.objects.filter(is_superuser=True).first()
            )
            created += 1
    
    print(f"  ✅ Created {created} payments!")
    return created

def seed_meetings(count=5):
    """Seed meetings"""
    print(f"\n📅 Seeding {count} meetings...")
    created = 0
    superuser = User.objects.filter(is_superuser=True).first()
    
    for i in range(count):
        date = timezone.now() + timedelta(days=random.randint(-30, 60))
        meeting = Meeting.objects.create(
            title=f"Meeting #{i+1}",
            date=date,
            venue=random.choice(['Conference Room A', 'Hall B', 'Online (Zoom)', 'Community Center']),
            agenda=f"Agenda items for meeting {i+1}...",
            status=random.choice(['scheduled', 'completed', 'completed', 'scheduled']),
            created_by=superuser or User.objects.first()
        )
        created += 1
        
        if random.choice([True, False]):
            members = Member.objects.filter(status='active')[:random.randint(5, 15)]
            for member in members:
                Attendance.objects.create(
                    meeting=meeting,
                    member=member,
                    status=random.choice(['present', 'present', 'present', 'absent', 'excused'])
                )
    
    print(f"  ✅ Created {created} meetings!")
    return created

def seed_all():
    """Seed all data"""
    print("=" * 60)
    print("LAKCHOGO CONNECT - DATA SEEDER")
    print("=" * 60)
    
    if Member.objects.count() > 0:
        confirm = input(f"\n⚠️ {Member.objects.count()} members already exist. Continue? (y/n): ")
        if confirm.lower() != 'y':
            print("❌ Seeding cancelled.")
            return
    
    members_count = seed_members(20)
    payments_count = seed_payments(members_count)
    meetings_count = seed_meetings(5)
    
    print("\n" + "=" * 60)
    print("✅ SEEDING COMPLETE!")
    print("=" * 60)
    print(f"\n📊 Summary:")
    print(f"  • Members: {Member.objects.count()}")
    print(f"  • Payments: {Payment.objects.count()}")
    print(f"  • Meetings: {Meeting.objects.count()}")
    print(f"  • Attendances: {Attendance.objects.count()}")
    print("\n🔑 Test Credentials:")
    print("  • Username: Any seeded user (e.g., john.kamau1)")
    print("  • Password: Test123456")
    print("=" * 60)

if __name__ == '__main__':
    seed_all()
