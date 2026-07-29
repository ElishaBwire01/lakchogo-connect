from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
import re

def validate_kenyan_phone(value):
    """Validate Kenyan phone number"""
    phone = re.sub(r'[\s\-\(\)\+]', '', value)
    
    pattern = r'^(254|0)[17]\d{8}$'
    if not re.match(pattern, phone):
        raise ValidationError(
            'Invalid Kenyan phone number. Must start with 254 or 0, followed by 7 or 1, then 8 digits.'
        )
    return value

def validate_id_number(value):
    """Validate Kenyan ID number"""
    id_num = re.sub(r'\s', '', value)
    
    if not re.match(r'^\d{8}$', id_num):
        raise ValidationError('ID number must be 8 digits for Kenyan National ID.')
    return value

def validate_password_strength(value):
    """Validate password strength"""
    if len(value) < 8:
        raise ValidationError('Password must be at least 8 characters long.')
    
    if not re.search(r'[A-Z]', value):
        raise ValidationError('Password must contain at least one uppercase letter.')
    
    if not re.search(r'[a-z]', value):
        raise ValidationError('Password must contain at least one lowercase letter.')
    
    if not re.search(r'\d', value):
        raise ValidationError('Password must contain at least one digit.')
    
    return value

phone_validator = RegexValidator(
    regex=r'^\+?254\d{9}$',
    message='Phone number must be in format: +254XXXXXXXXX or 07XXXXXXXX'
)
