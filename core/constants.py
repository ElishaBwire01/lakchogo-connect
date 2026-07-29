"""
Constants used across the application
Centralized location for all constant values
"""

# ============================================
# USER & ROLE CONSTANTS
# ============================================

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

DEFAULT_ROLES = ['Admin', 'Treasurer', 'Secretary', 'Welfare Officer', 'Member']

# ============================================
# PAYMENT CONSTANTS
# ============================================

PAYMENT_STATUS_PENDING = 'pending'
PAYMENT_STATUS_COMPLETED = 'completed'
PAYMENT_STATUS_FAILED = 'failed'
PAYMENT_STATUS_REFUNDED = 'refunded'
PAYMENT_STATUS_CANCELLED = 'cancelled'

PAYMENT_STATUS_CHOICES = [
    (PAYMENT_STATUS_PENDING, 'Pending'),
    (PAYMENT_STATUS_COMPLETED, 'Completed'),
    (PAYMENT_STATUS_FAILED, 'Failed'),
    (PAYMENT_STATUS_REFUNDED, 'Refunded'),
    (PAYMENT_STATUS_CANCELLED, 'Cancelled'),
]

PAYMENT_METHOD_MPESA = 'mpesa'
PAYMENT_METHOD_AIRTEL = 'airtel'
PAYMENT_METHOD_CASH = 'cash'
PAYMENT_METHOD_BANK = 'bank'
PAYMENT_METHOD_CHEQUE = 'cheque'
PAYMENT_METHOD_OTHER = 'other'

PAYMENT_METHOD_CHOICES = [
    (PAYMENT_METHOD_MPESA, 'M-Pesa'),
    (PAYMENT_METHOD_AIRTEL, 'Airtel Money'),
    (PAYMENT_METHOD_CASH, 'Cash'),
    (PAYMENT_METHOD_BANK, 'Bank Transfer'),
    (PAYMENT_METHOD_CHEQUE, 'Cheque'),
    (PAYMENT_METHOD_OTHER, 'Other'),
]

PAYMENT_FREQUENCY_MONTHLY = 'monthly'
PAYMENT_FREQUENCY_YEARLY = 'yearly'
PAYMENT_FREQUENCY_ONE_TIME = 'one-time'
PAYMENT_FREQUENCY_QUARTERLY = 'quarterly'
PAYMENT_FREQUENCY_WEEKLY = 'weekly'

PAYMENT_FREQUENCY_CHOICES = [
    (PAYMENT_FREQUENCY_MONTHLY, 'Monthly'),
    (PAYMENT_FREQUENCY_YEARLY, 'Yearly'),
    (PAYMENT_FREQUENCY_ONE_TIME, 'One-Time'),
    (PAYMENT_FREQUENCY_QUARTERLY, 'Quarterly'),
    (PAYMENT_FREQUENCY_WEEKLY, 'Weekly'),
]

# ============================================
# MEETING CONSTANTS
# ============================================

MEETING_STATUS_SCHEDULED = 'scheduled'
MEETING_STATUS_ONGOING = 'ongoing'
MEETING_STATUS_COMPLETED = 'completed'
MEETING_STATUS_CANCELLED = 'cancelled'

MEETING_STATUS_CHOICES = [
    (MEETING_STATUS_SCHEDULED, 'Scheduled'),
    (MEETING_STATUS_ONGOING, 'Ongoing'),
    (MEETING_STATUS_COMPLETED, 'Completed'),
    (MEETING_STATUS_CANCELLED, 'Cancelled'),
]

ATTENDANCE_STATUS_PRESENT = 'present'
ATTENDANCE_STATUS_ABSENT = 'absent'
ATTENDANCE_STATUS_EXCUSED = 'excused'
ATTENDANCE_STATUS_LATE = 'late'

ATTENDANCE_STATUS_CHOICES = [
    (ATTENDANCE_STATUS_PRESENT, 'Present'),
    (ATTENDANCE_STATUS_ABSENT, 'Absent'),
    (ATTENDANCE_STATUS_EXCUSED, 'Excused'),
    (ATTENDANCE_STATUS_LATE, 'Late'),
]

ATTENDANCE_CHECK_IN_QR = 'qr'
ATTENDANCE_CHECK_IN_MANUAL = 'manual'
ATTENDANCE_CHECK_IN_GPS = 'gps'
ATTENDANCE_CHECK_IN_FINGERPRINT = 'fingerprint'

ATTENDANCE_CHECK_IN_CHOICES = [
    (ATTENDANCE_CHECK_IN_QR, 'QR Code'),
    (ATTENDANCE_CHECK_IN_MANUAL, 'Manual'),
    (ATTENDANCE_CHECK_IN_GPS, 'GPS'),
    (ATTENDANCE_CHECK_IN_FINGERPRINT, 'Fingerprint'),
]

# ============================================
# COMPLIANCE CONSTANTS
# ============================================

COMPLIANCE_STATUS_GREEN = 'green'
COMPLIANCE_STATUS_YELLOW = 'yellow'
COMPLIANCE_STATUS_RED = 'red'

COMPLIANCE_STATUS_CHOICES = [
    (COMPLIANCE_STATUS_GREEN, 'Eligible'),
    (COMPLIANCE_STATUS_YELLOW, 'Warning'),
    (COMPLIANCE_STATUS_RED, 'Not Eligible'),
]

COMPLIANCE_RULE_TYPE_PAYMENT = 'payment'
COMPLIANCE_RULE_TYPE_ATTENDANCE = 'attendance'
COMPLIANCE_RULE_TYPE_COMBINED = 'combined'

COMPLIANCE_RULE_TYPE_CHOICES = [
    (COMPLIANCE_RULE_TYPE_PAYMENT, 'Payment'),
    (COMPLIANCE_RULE_TYPE_ATTENDANCE, 'Attendance'),
    (COMPLIANCE_RULE_TYPE_COMBINED, 'Combined'),
]

COMPLIANCE_ALERT_TYPE_PAYMENT_OVERDUE = 'payment_overdue'
COMPLIANCE_ALERT_TYPE_ATTENDANCE_LOW = 'attendance_low'
COMPLIANCE_ALERT_TYPE_COMPLIANCE_LOW = 'compliance_low'
COMPLIANCE_ALERT_TYPE_STATUS_CHANGED = 'status_changed'
COMPLIANCE_ALERT_TYPE_WARNING_ISSUED = 'warning_issued'

COMPLIANCE_ALERT_TYPE_CHOICES = [
    (COMPLIANCE_ALERT_TYPE_PAYMENT_OVERDUE, 'Payment Overdue'),
    (COMPLIANCE_ALERT_TYPE_ATTENDANCE_LOW, 'Low Attendance'),
    (COMPLIANCE_ALERT_TYPE_COMPLIANCE_LOW, 'Low Compliance Score'),
    (COMPLIANCE_ALERT_TYPE_STATUS_CHANGED, 'Status Changed'),
    (COMPLIANCE_ALERT_TYPE_WARNING_ISSUED, 'Warning Issued'),
]

# ============================================
# WELFARE CONSTANTS
# ============================================

BEREAVEMENT_STATUS_ACTIVE = 'active'
BEREAVEMENT_STATUS_CLOSED = 'closed'
BEREAVEMENT_STATUS_DISBURSED = 'disbursed'
BEREAVEMENT_STATUS_CANCELLED = 'cancelled'

BEREAVEMENT_STATUS_CHOICES = [
    (BEREAVEMENT_STATUS_ACTIVE, 'Active'),
    (BEREAVEMENT_STATUS_CLOSED, 'Closed'),
    (BEREAVEMENT_STATUS_DISBURSED, 'Disbursed'),
    (BEREAVEMENT_STATUS_CANCELLED, 'Cancelled'),
]

CONTRIBUTION_TYPE_MEMBER = 'member'
CONTRIBUTION_TYPE_PUBLIC = 'public'
CONTRIBUTION_TYPE_GROUP = 'group'
CONTRIBUTION_TYPE_OTHER = 'other'

CONTRIBUTION_TYPE_CHOICES = [
    (CONTRIBUTION_TYPE_MEMBER, 'Member Contribution'),
    (CONTRIBUTION_TYPE_PUBLIC, 'Public Contribution'),
    (CONTRIBUTION_TYPE_GROUP, 'Group Contribution'),
    (CONTRIBUTION_TYPE_OTHER, 'Other'),
]

# ============================================
# COMMUNICATION CONSTANTS
# ============================================

NOTIFICATION_TYPE_PAYMENT_REMINDER = 'payment_reminder'
NOTIFICATION_TYPE_ATTENDANCE_ALERT = 'attendance_alert'
NOTIFICATION_TYPE_MEETING_REMINDER = 'meeting_reminder'
NOTIFICATION_TYPE_WELFARE_ALERT = 'welfare_alert'
NOTIFICATION_TYPE_COMPLIANCE_ALERT = 'compliance_alert'
NOTIFICATION_TYPE_SYSTEM = 'system'
NOTIFICATION_TYPE_ANNOUNCEMENT = 'announcement'

NOTIFICATION_TYPE_CHOICES = [
    (NOTIFICATION_TYPE_PAYMENT_REMINDER, 'Payment Reminder'),
    (NOTIFICATION_TYPE_ATTENDANCE_ALERT, 'Attendance Alert'),
    (NOTIFICATION_TYPE_MEETING_REMINDER, 'Meeting Reminder'),
    (NOTIFICATION_TYPE_WELFARE_ALERT, 'Welfare Alert'),
    (NOTIFICATION_TYPE_COMPLIANCE_ALERT, 'Compliance Alert'),
    (NOTIFICATION_TYPE_SYSTEM, 'System Notification'),
    (NOTIFICATION_TYPE_ANNOUNCEMENT, 'Announcement'),
]

NOTIFICATION_CHANNEL_PUSH = 'push'
NOTIFICATION_CHANNEL_SMS = 'sms'
NOTIFICATION_CHANNEL_EMAIL = 'email'
NOTIFICATION_CHANNEL_IN_APP = 'in_app'

NOTIFICATION_CHANNEL_CHOICES = [
    (NOTIFICATION_CHANNEL_PUSH, 'Push Notification'),
    (NOTIFICATION_CHANNEL_SMS, 'SMS'),
    (NOTIFICATION_CHANNEL_EMAIL, 'Email'),
    (NOTIFICATION_CHANNEL_IN_APP, 'In-App'),
]

NOTIFICATION_PRIORITY_LOW = 'low'
NOTIFICATION_PRIORITY_NORMAL = 'normal'
NOTIFICATION_PRIORITY_HIGH = 'high'
NOTIFICATION_PRIORITY_URGENT = 'urgent'

NOTIFICATION_PRIORITY_CHOICES = [
    (NOTIFICATION_PRIORITY_LOW, 'Low'),
    (NOTIFICATION_PRIORITY_NORMAL, 'Normal'),
    (NOTIFICATION_PRIORITY_HIGH, 'High'),
    (NOTIFICATION_PRIORITY_URGENT, 'Urgent'),
]

# ============================================
# MEMBER CONSTANTS
# ============================================

MEMBER_STATUS_ACTIVE = 'active'
MEMBER_STATUS_INACTIVE = 'inactive'
MEMBER_STATUS_SUSPENDED = 'suspended'
MEMBER_STATUS_PENDING = 'pending'

MEMBER_STATUS_CHOICES = [
    (MEMBER_STATUS_ACTIVE, 'Active'),
    (MEMBER_STATUS_INACTIVE, 'Inactive'),
    (MEMBER_STATUS_SUSPENDED, 'Suspended'),
    (MEMBER_STATUS_PENDING, 'Pending'),
]

MEMBER_GENDER_MALE = 'male'
MEMBER_GENDER_FEMALE = 'female'
MEMBER_GENDER_OTHER = 'other'

MEMBER_GENDER_CHOICES = [
    (MEMBER_GENDER_MALE, 'Male'),
    (MEMBER_GENDER_FEMALE, 'Female'),
    (MEMBER_GENDER_OTHER, 'Other'),
]

# ============================================
# REPORT CONSTANTS
# ============================================

REPORT_TYPE_MEMBER = 'member'
REPORT_TYPE_PAYMENT = 'payment'
REPORT_TYPE_ATTENDANCE = 'attendance'
REPORT_TYPE_COMPLIANCE = 'compliance'
REPORT_TYPE_WELFARE = 'welfare'
REPORT_TYPE_SUMMARY = 'summary'

REPORT_TYPE_CHOICES = [
    (REPORT_TYPE_MEMBER, 'Member Report'),
    (REPORT_TYPE_PAYMENT, 'Payment Report'),
    (REPORT_TYPE_ATTENDANCE, 'Attendance Report'),
    (REPORT_TYPE_COMPLIANCE, 'Compliance Report'),
    (REPORT_TYPE_WELFARE, 'Welfare Report'),
    (REPORT_TYPE_SUMMARY, 'Summary Report'),
]

# ============================================
# GENERAL CONSTANTS
# ============================================

DEFAULT_PAGE_SIZE = 20
MAX_PAGE_SIZE = 100

DATE_FORMAT = '%Y-%m-%d'
DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S'
TIME_FORMAT = '%H:%M:%S'

CURRENCY_SYMBOL = 'KES'
CURRENCY_CODE = 'KES'

# API Constants
API_VERSION = 'v1'
API_PREFIX = 'api'

# Cache Keys
CACHE_KEY_MEMBERS = 'members_list'
CACHE_KEY_PAYMENTS = 'payments_list'
CACHE_KEY_MEETINGS = 'meetings_list'
CACHE_KEY_COMPLIANCE = 'compliance_stats'
CACHE_KEY_WELFARE = 'welfare_stats'

# Session Keys
SESSION_KEY_RESET_CODE = 'reset_code'
SESSION_KEY_RESET_USER_ID = 'reset_user_id'

# File Upload Constants
MAX_UPLOAD_SIZE = 5 * 1024 * 1024  # 5MB
ALLOWED_IMAGE_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.gif', '.svg']
ALLOWED_DOCUMENT_EXTENSIONS = ['.pdf', '.doc', '.docx', '.txt', '.csv', '.xls', '.xlsx']
