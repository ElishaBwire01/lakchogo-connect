# Application constants

ROLE_ADMIN = 'Admin'
ROLE_TREASURER = 'Treasurer'
ROLE_SECRETARY = 'Secretary'
ROLE_WELFARE_OFFICER = 'Welfare Officer'
ROLE_MEMBER = 'Member'

ROLE_CHOICES = [
    (ROLE_ADMIN, 'Administrator'),
    (ROLE_TREASURER, 'Treasurer'),
    (ROLE_SECRETARY, 'Secretary'),
    (ROLE_WELFARE_OFFICER, 'Welfare Officer'),
    (ROLE_MEMBER, 'Member'),
]

PAYMENT_STATUS_CHOICES = [
    ('pending', 'Pending'),
    ('completed', 'Completed'),
    ('failed', 'Failed'),
    ('refunded', 'Refunded'),
]

MEETING_STATUS_CHOICES = [
    ('scheduled', 'Scheduled'),
    ('ongoing', 'Ongoing'),
    ('completed', 'Completed'),
    ('cancelled', 'Cancelled'),
]

ATTENDANCE_STATUS_CHOICES = [
    ('present', 'Present'),
    ('absent', 'Absent'),
    ('excused', 'Excused'),
]

COMPLIANCE_STATUS_CHOICES = [
    ('green', 'Eligible'),
    ('yellow', 'Warning'),
    ('red', 'Not Eligible'),
]
