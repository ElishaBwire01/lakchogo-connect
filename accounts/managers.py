from django.contrib.auth.base_user import BaseUserManager
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

class UserManager(BaseUserManager):
    """Custom user manager for User model"""
    
    def create_user(self, username, phone, password=None, **extra_fields):
        """Create and save a regular user"""
        if not username:
            raise ValueError(_('Username is required'))
        if not phone:
            raise ValueError(_('Phone number is required'))
            
        user = self.model(
            username=username,
            phone=phone,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, username, phone, password=None, **extra_fields):
        """Create and save a superuser"""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))
        
        return self.create_user(username, phone, password, **extra_fields)
    
    def get_by_phone(self, phone):
        """Get user by phone number"""
        try:
            return self.get(phone=phone)
        except self.model.DoesNotExist:
            return None
    
    def get_active_members(self):
        """Get all active members"""
        return self.filter(is_active=True)
    
    def get_committee_members(self):
        """Get all committee members"""
        return self.filter(is_committee=True)
