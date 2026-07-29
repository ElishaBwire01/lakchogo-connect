"""
Custom exceptions for LakChogo Connect
"""

class LakChogoException(Exception):
    """Base exception for LakChogo Connect"""
    pass


class AuthenticationFailed(LakChogoException):
    """Raised when authentication fails"""
    pass


class PermissionDenied(LakChogoException):
    """Raised when user doesn't have permission"""
    pass


class NotFound(LakChogoException):
    """Raised when a resource is not found"""
    pass


class ValidationError(LakChogoException):
    """Raised when validation fails"""
    pass


class DuplicateError(LakChogoException):
    """Raised when a duplicate resource is created"""
    pass


class PaymentError(LakChogoException):
    """Raised when a payment operation fails"""
    pass


class ComplianceError(LakChogoException):
    """Raised when a compliance operation fails"""
    pass


class WelfareError(LakChogoException):
    """Raised when a welfare operation fails"""
    pass


class MeetingError(LakChogoException):
    """Raised when a meeting operation fails"""
    pass


class MemberError(LakChogoException):
    """Raised when a member operation fails"""
    pass


class ReportError(LakChogoException):
    """Raised when a report operation fails"""
    pass


class NotificationError(LakChogoException):
    """Raised when a notification operation fails"""
    pass


class QRCodeError(LakChogoException):
    """Raised when QR code generation fails"""
    pass
