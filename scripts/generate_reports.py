#!/usr/bin/env python
"""
Report generation script for LakChogo Connect.
Run this script to generate various reports.
"""

import os
import sys
import django
import csv
import json
from datetime import datetime, timedelta

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lakchogo.settings')
django.setup()

from members.models import Member
from finance.models import Payment, PaymentCategory
from meetings.models import Meeting, Attendance
from compliance.models import ComplianceScore
from welfare.models import BereavementEvent

def generate_member_report():
    print("\n👤 Generating Member Report...")
    members = Member.objects.all().order_by('-date_joined')
    filename = f"reports/member_report_{datetime.now().strftime('%Y%m%d')}.csv"
    os.makedirs('reports', exist_ok=True)
    
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Member ID', 'Name', 'Phone', 'Status', 'Compliance', 'Joined'])
        for member in members:
            writer.writerow([
                member.member_id,
                member.get_full_name(),
                member.user.phone,
                member.status,
                member.compliance_status,
                member.date_joined.strftime('%Y-%m-%d')
            ])
    print(f"  ✅ Member report saved to: {filename}")
    return filename

def generate_payment_report():
    print("\n💰 Generating Payment Report...")
    payments = Payment.objects.filter(status='completed').order_by('-created_at')
    filename = f"reports/payment_report_{datetime.now().strftime('%Y%m%d')}.csv"
    os.makedirs('reports', exist_ok=True)
    
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Payment ID', 'Member', 'Category', 'Amount', 'Method', 'Date'])
        for payment in payments:
            writer.writerow([
                payment.id,
                payment.member.get_full_name(),
                payment.category.name,
                payment.amount,
                payment.get_payment_method_display(),
                payment.created_at.strftime('%Y-%m-%d %H:%M')
            ])
    print(f"  ✅ Payment report saved to: {filename}")
    return filename

def generate_attendance_report():
    print("\n📅 Generating Attendance Report...")
    meetings = Meeting.objects.filter(status='completed').order_by('-date')
    filename = f"reports/attendance_report_{datetime.now().strftime('%Y%m%d')}.csv"
    os.makedirs('reports', exist_ok=True)
    
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Meeting', 'Date', 'Member', 'Status', 'Check-in Method', 'Check-in Time'])
        for meeting in meetings:
            attendances = Attendance.objects.filter(meeting=meeting)
            for attendance in attendances:
                writer.writerow([
                    meeting.title,
                    meeting.date.strftime('%Y-%m-%d %H:%M'),
                    attendance.member.get_full_name(),
                    attendance.status,
                    attendance.check_in_method or '',
                    attendance.check_in_time.strftime('%H:%M') if attendance.check_in_time else ''
                ])
    print(f"  ✅ Attendance report saved to: {filename}")
    return filename

def generate_compliance_report():
    print("\n📋 Generating Compliance Report...")
    scores = ComplianceScore.objects.all().order_by('-score')
    filename = f"reports/compliance_report_{datetime.now().strftime('%Y%m%d')}.csv"
    os.makedirs('reports', exist_ok=True)
    
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Member ID', 'Name', 'Status', 'Score', 'Payment Score', 'Attendance Score', 'Warnings'])
        for score in scores:
            writer.writerow([
                score.member.member_id,
                score.member.get_full_name(),
                score.status,
                score.score,
                score.payment_compliance,
                score.attendance_compliance,
                len(score.warnings)
            ])
    print(f"  ✅ Compliance report saved to: {filename}")
    return filename

def generate_welfare_report():
    print("\n❤️ Generating Welfare Report...")
    events = BereavementEvent.objects.all().order_by('-created_at')
    filename = f"reports/welfare_report_{datetime.now().strftime('%Y%m%d')}.csv"
    os.makedirs('reports', exist_ok=True)
    
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Event Code', 'Member', 'Deceased', 'Relationship', 'Collection Target', 'Amount Collected', 'Status', 'Progress'])
        for event in events:
            writer.writerow([
                event.event_code,
                event.member.get_full_name(),
                event.deceased_name,
                event.relationship,
                event.collection_target,
                event.amount_collected,
                event.status,
                f"{event.progress_percentage:.1f}%"
            ])
    print(f"  ✅ Welfare report saved to: {filename}")
    return filename

def generate_summary_json():
    print("\n📊 Generating Summary JSON...")
    total_members = Member.objects.count()
    active_members = Member.objects.filter(status='active').count()
    
    data = {
        'generated_at': datetime.now().isoformat(),
        'members': {
            'total': total_members,
            'active': active_members,
            'pending': Member.objects.filter(status='pending').count(),
            'inactive': Member.objects.filter(status='inactive').count(),
        },
        'payments': {
            'total': Payment.objects.filter(status='completed').count(),
            'pending': Payment.objects.filter(status='pending').count(),
        },
        'meetings': {
            'total': Meeting.objects.count(),
            'scheduled': Meeting.objects.filter(status='scheduled').count(),
            'completed': Meeting.objects.filter(status='completed').count(),
        },
        'compliance': {
            'green': ComplianceScore.objects.filter(status='green').count(),
            'yellow': ComplianceScore.objects.filter(status='yellow').count(),
            'red': ComplianceScore.objects.filter(status='red').count(),
        }
    }
    
    filename = f"reports/summary_{datetime.now().strftime('%Y%m%d')}.json"
    os.makedirs('reports', exist_ok=True)
    
    with open(filename, 'w') as f:
        json.dump(data, f, indent=2)
    print(f"  ✅ Summary saved to: {filename}")
    return filename

def generate_all_reports():
    print("=" * 60)
    print("LAKCHOGO CONNECT - REPORT GENERATOR")
    print("=" * 60)
    
    reports = [
        generate_member_report(),
        generate_payment_report(),
        generate_attendance_report(),
        generate_compliance_report(),
        generate_welfare_report(),
        generate_summary_json()
    ]
    
    print("\n" + "=" * 60)
    print("✅ REPORTS GENERATED!")
    print("=" * 60)
    print("\n📊 Generated Reports:")
    for report in reports:
        print(f"  • {report}")
    print("\n📁 Reports saved in 'reports/' directory")
    print("=" * 60)

if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1:
        command = sys.argv[1]
        if command == 'members':
            generate_member_report()
        elif command == 'payments':
            generate_payment_report()
        elif command == 'attendance':
            generate_attendance_report()
        elif command == 'compliance':
            generate_compliance_report()
        elif command == 'welfare':
            generate_welfare_report()
        elif command == 'summary':
            generate_summary_json()
        else:
            generate_all_reports()
    else:
        generate_all_reports()
