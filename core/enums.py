"""
Enum classes for LakChogo Connect
Provides type-safe enumerations for various fields
"""

from enum import Enum

class RoleType(Enum):
    """User role types"""
    ADMIN = 'Admin'
    TREASURER = 'Treasurer'
    SECRETARY = 'Secretary'
    WELFARE_OFFICER = 'Welfare Officer'
    MEMBER = 'Member'

    @classmethod
    def choices(cls):
        return [(item.value, item.name.replace('_', ' ').title()) for item in cls]


class PaymentStatus(Enum):
    """Payment status types"""
    PENDING = 'pending'
    COMPLETED = 'completed'
    FAILED = 'failed'
    REFUNDED = 'refunded'
    CANCELLED = 'cancelled'

    @classmethod
    def choices(cls):
        return [(item.value, item.name.title()) for item in cls]


class PaymentMethod(Enum):
    """Payment method types"""
    MPESA = 'mpesa'
    AIRTEL = 'airtel'
    CASH = 'cash'
    BANK = 'bank'
    CHEQUE = 'cheque'
    OTHER = 'other'

    @classmethod
    def choices(cls):
        return [(item.value, item.name.title()) for item in cls]


class PaymentFrequency(Enum):
    """Payment frequency types"""
    MONTHLY = 'monthly'
    YEARLY = 'yearly'
    ONE_TIME = 'one-time'
    QUARTERLY = 'quarterly'
    WEEKLY = 'weekly'

    @classmethod
    def choices(cls):
        return [(item.value, item.name.replace('_', ' ').title()) for item in cls]


class MeetingStatus(Enum):
    """Meeting status types"""
    SCHEDULED = 'scheduled'
    ONGOING = 'ongoing'
    COMPLETED = 'completed'
    CANCELLED = 'cancelled'

    @classmethod
    def choices(cls):
        return [(item.value, item.name.title()) for item in cls]


class AttendanceStatus(Enum):
    """Attendance status types"""
    PRESENT = 'present'
    ABSENT = 'absent'
    EXCUSED = 'excused'
    LATE = 'late'

    @classmethod
    def choices(cls):
        return [(item.value, item.name.title()) for item in cls]


class ComplianceStatus(Enum):
    """Compliance status types"""
    GREEN = 'green'
    YELLOW = 'yellow'
    RED = 'red'

    @classmethod
    def choices(cls):
        return [
            (cls.GREEN.value, 'Eligible'),
            (cls.YELLOW.value, 'Warning'),
            (cls.RED.value, 'Not Eligible'),
        ]


class MemberStatus(Enum):
    """Member status types"""
    ACTIVE = 'active'
    INACTIVE = 'inactive'
    SUSPENDED = 'suspended'
    PENDING = 'pending'

    @classmethod
    def choices(cls):
        return [(item.value, item.name.title()) for item in cls]


class NotificationType(Enum):
    """Notification type types"""
    PAYMENT_REMINDER = 'payment_reminder'
    ATTENDANCE_ALERT = 'attendance_alert'
    MEETING_REMINDER = 'meeting_reminder'
    WELFARE_ALERT = 'welfare_alert'
    COMPLIANCE_ALERT = 'compliance_alert'
    SYSTEM = 'system'
    ANNOUNCEMENT = 'announcement'

    @classmethod
    def choices(cls):
        return [(item.value, item.name.replace('_', ' ').title()) for item in cls]


class NotificationPriority(Enum):
    """Notification priority types"""
    LOW = 'low'
    NORMAL = 'normal'
    HIGH = 'high'
    URGENT = 'urgent'

    @classmethod
    def choices(cls):
        return [(item.value, item.name.title()) for item in cls]


class BereavementStatus(Enum):
    """Bereavement event status types"""
    ACTIVE = 'active'
    CLOSED = 'closed'
    DISBURSED = 'disbursed'
    CANCELLED = 'cancelled'

    @classmethod
    def choices(cls):
        return [(item.value, item.name.title()) for item in cls]


class Gender(Enum):
    """Gender types"""
    MALE = 'male'
    FEMALE = 'female'
    OTHER = 'other'

    @classmethod
    def choices(cls):
        return [(item.value, item.name.title()) for item in cls]


class ReportType(Enum):
    """Report type types"""
    MEMBER = 'member'
    PAYMENT = 'payment'
    ATTENDANCE = 'attendance'
    COMPLIANCE = 'compliance'
    WELFARE = 'welfare'
    SUMMARY = 'summary'

    @classmethod
    def choices(cls):
        return [(item.value, item.name.title()) for item in cls]
