"""
Utility functions for LakChogo Connect
"""

import re
import random
import string
import hashlib
from datetime import datetime, timedelta
from decimal import Decimal
from django.utils import timezone

def generate_member_id():
    """Generate a unique member ID"""
    import time
    timestamp = str(int(time.time()))[-4:]
    random_part = ''.join(random.choices(string.digits, k=4))
    return f"LCG-{timestamp}{random_part}"

def generate_receipt_number():
    """Generate a unique receipt number"""
    import time
    timestamp = str(int(time.time()))
    random_part = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    return f"REC-{timestamp[-6:]}{random_part}"

def generate_event_code():
    """Generate a unique event code"""
    import time
    year = timezone.now().year
    random_part = ''.join(random.choices(string.digits, k=4))
    return f"E-{year}-{random_part}"

def generate_transaction_ref():
    """Generate a unique transaction reference"""
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    random_part = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    return f"TXN-{timestamp}-{random_part}"

def generate_reset_code():
    """Generate a 6-digit reset code"""
    return ''.join(random.choices(string.digits, k=6))

def generate_otp():
    """Generate a 6-digit OTP"""
    return ''.join(random.choices(string.digits, k=6))

def format_currency(amount):
    """Format amount as currency"""
    return f"KES {amount:,.2f}"

def format_phone(phone):
    """Format phone number"""
    # Remove all non-digit characters
    phone = re.sub(r'\D', '', phone)
    
    # Format based on length
    if len(phone) == 10 and phone.startswith('0'):
        return f"+254{phone[1:]}"
    elif len(phone) == 12 and phone.startswith('254'):
        return f"+{phone}"
    elif len(phone) == 11 and phone.startswith('254'):
        return f"+{phone}"
    else:
        return phone

def calculate_percentage(part, total):
    """Calculate percentage"""
    if total == 0:
        return 0
    return (part / total) * 100

def calculate_compliance_score(payment_score, attendance_score, weights=None):
    """Calculate overall compliance score"""
    if weights is None:
        weights = {'payment': 0.5, 'attendance': 0.5}
    
    score = (payment_score * weights['payment']) + (attendance_score * weights['attendance'])
    return min(100, max(0, score))

def get_compliance_status(score):
    """Get compliance status based on score"""
    if score >= 80:
        return 'green'
    elif score >= 60:
        return 'yellow'
    else:
        return 'red'

def truncate_text(text, length=100, suffix='...'):
    """Truncate text to a certain length"""
    if len(text) <= length:
        return text
    return text[:length] + suffix

def safe_divide(numerator, denominator, default=0):
    """Safe division to avoid ZeroDivisionError"""
    try:
        return numerator / denominator
    except ZeroDivisionError:
        return default

def parse_date(date_string, format='%Y-%m-%d'):
    """Parse date string to datetime object"""
    try:
        return datetime.strptime(date_string, format).date()
    except (ValueError, TypeError):
        return None

def format_datetime(dt, format='%Y-%m-%d %H:%M:%S'):
    """Format datetime object to string"""
    if dt is None:
        return ''
    return dt.strftime(format)

def get_today():
    """Get today's date"""
    return timezone.now().date()

def get_now():
    """Get current datetime"""
    return timezone.now()

def days_between(date1, date2):
    """Calculate days between two dates"""
    if date1 and date2:
        return (date2 - date1).days
    return 0

def is_within_grace_period(date, days=30):
    """Check if a date is within grace period"""
    if date:
        return (get_today() - date).days <= days
    return False

def generate_slug(text):
    """Generate a slug from text"""
    text = text.lower()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[-\s]+', '-', text)
    return text.strip('-')

def mask_email(email):
    """Mask email for privacy"""
    if '@' not in email:
        return email
    local, domain = email.split('@')
    if len(local) <= 2:
        local_masked = local[0] + '***'
    else:
        local_masked = local[0] + '***' + local[-1]
    return f"{local_masked}@{domain}"

def mask_phone(phone):
    """Mask phone number for privacy"""
    if len(phone) <= 4:
        return phone
    return phone[:3] + '***' + phone[-3:]
