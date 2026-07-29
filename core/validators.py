"""
Custom validators for LakChogo Connect
Used for validating form and model data
"""

import re
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _


def validate_kenyan_phone(value):
    """
    Validate Kenyan phone number
    Format: +254XXXXXXXXX or 07XXXXXXXX or 01XXXXXXXX
    """
    # Remove spaces and special characters
    phone = re.sub(r'[\s\-\(\)]', '', value)
    
    # Kenyan phone patterns
    patterns = [
        r'^254[17]\d{8}$',  # +2547xxxxxxxx or +2541xxxxxxxx
        r'^0[17]\d{8}$',    # 07xxxxxxxx or 01xxxxxxxx
    ]
    
    for pattern in patterns:
        if re.match(pattern, phone):
            return value
    
    raise ValidationError(
        _('Invalid Kenyan phone number. Must start with 254 or 0, followed by 7 or 1, then 8 digits.')
    )


def validate_kenyan_id(value):
    """
    Validate Kenyan ID number
    Format: 8 digits
    """
    id_num = re.sub(r'\s', '', value)
    
    if not re.match(r'^\d{8}$', id_num):
        raise ValidationError(_('ID number must be 8 digits.'))
    
    return value


def validate_password_strength(value):
    """
    Validate password strength
    - At least 8 characters
    - At least one uppercase letter
    - At least one lowercase letter
    - At least one digit
    """
    if len(value) < 8:
        raise ValidationError(_('Password must be at least 8 characters long.'))
    
    if not re.search(r'[A-Z]', value):
        raise ValidationError(_('Password must contain at least one uppercase letter.'))
    
    if not re.search(r'[a-z]', value):
        raise ValidationError(_('Password must contain at least one lowercase letter.'))
    
    if not re.search(r'\d', value):
        raise ValidationError(_('Password must contain at least one digit.'))
    
    return value


def validate_file_size(value, max_size=5 * 1024 * 1024):
    """
    Validate file size
    Default max size: 5MB
    """
    if value.size > max_size:
        raise ValidationError(
            _(f'File size must be less than {max_size / (1024 * 1024):.0f}MB.')
        )
    return value


def validate_image_extension(value):
    """
    Validate image file extension
    Allowed: .jpg, .jpeg, .png, .gif, .svg
    """
    allowed_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.svg']
    ext = '.' + value.name.split('.')[-1].lower()
    
    if ext not in allowed_extensions:
        raise ValidationError(
            _(f'File extension must be one of: {", ".join(allowed_extensions)}')
        )
    return value


def validate_document_extension(value):
    """
    Validate document file extension
    Allowed: .pdf, .doc, .docx, .txt, .csv, .xls, .xlsx
    """
    allowed_extensions = ['.pdf', '.doc', '.docx', '.txt', '.csv', '.xls', '.xlsx']
    ext = '.' + value.name.split('.')[-1].lower()
    
    if ext not in allowed_extensions:
        raise ValidationError(
            _(f'File extension must be one of: {", ".join(allowed_extensions)}')
        )
    return value


# Predefined validators for models
phone_validator = RegexValidator(
    regex=r'^\+?254\d{9}$',
    message=_('Phone number must be in format: +254XXXXXXXXX or 07XXXXXXXX')
)

email_validator = RegexValidator(
    regex=r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',
    message=_('Enter a valid email address.')
)

member_id_validator = RegexValidator(
    regex=r'^LCG-\d{4}$',
    message=_('Member ID must be in format: LCG-XXXX (e.g., LCG-0001)')
)
