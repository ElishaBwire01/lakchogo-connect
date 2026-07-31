from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.core.validators import RegexValidator
from django.utils import timezone
from django.conf import settings

class User(AbstractUser):
    """Custom User model with phone number and role"""
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Phone number must be entered in the format: '+254XXXXXXXXX'."
    )
    
    phone = models.CharField(
        validators=[phone_regex], 
        max_length=17, 
        unique=True,
        help_text="Contact phone number"
    )
    id_number = models.CharField(
        max_length=20, 
        unique=True,
        help_text="National ID or Passport number"
    )
    date_joined = models.DateTimeField(default=timezone.now)
    is_active = models.BooleanField(default=True)
    is_committee = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    last_login = models.DateTimeField(null=True, blank=True)
    profile_picture = models.ImageField(
        upload_to='profile_pics/', 
        null=True, 
        blank=True
    )
    
    class Meta:
        db_table = 'users'
        ordering = ['-date_joined']
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def __str__(self):
        return f"{self.get_full_name()} ({self.phone})"

    def get_full_name(self):
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.username
    
    def has_permission(self, permission_codename):
        """Check if user has a specific permission"""
        from .permissions import user_has_permission
        return user_has_permission(self, permission_codename)
    
    def has_any_permission(self, permission_codenames):
        """Check if user has any of the listed permissions"""
        from .permissions import user_has_any_permission
        return user_has_any_permission(self, permission_codenames)
    
    def has_all_permissions(self, permission_codenames):
        """Check if user has all listed permissions"""
        from .permissions import user_has_all_permissions
        return user_has_all_permissions(self, permission_codenames)
    
    @property
    def is_admin(self):
        """Check if user is admin"""
        if self.is_superuser:
            return True
        return UserRole.objects.filter(
            user=self,
            role__name='Admin',
            is_active=True
        ).exists()
    
    @property
    def is_treasurer(self):
        if self.is_superuser:
            return True
        return UserRole.objects.filter(
            user=self,
            role__name='Treasurer',
            is_active=True
        ).exists()
    
    @property
    def is_secretary(self):
        if self.is_superuser:
            return True
        return UserRole.objects.filter(
            user=self,
            role__name='Secretary',
            is_active=True
        ).exists()
    
    @property
    def is_welfare_officer(self):
        if self.is_superuser:
            return True
        return UserRole.objects.filter(
            user=self,
            role__name='Welfare Officer',
            is_active=True
        ).exists()
    
    @property
    def is_committee_member(self):
        if self.is_superuser:
            return True
        return UserRole.objects.filter(
            user=self,
            role__name__in=['Admin', 'Treasurer', 'Secretary', 'Welfare Officer'],
            is_active=True
        ).exists()
    
    @property
    def is_member(self):
        return hasattr(self, 'member') and self.member.is_active


class Role(models.Model):
    """User roles: Admin, Treasurer, Secretary, Welfare Officer, Member"""
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)
    permissions = models.ManyToManyField(Permission, blank=True)
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'roles'
        ordering = ['name']
        verbose_name = 'Role'
        verbose_name_plural = 'Roles'

    def __str__(self):
        return self.name


class UserRole(models.Model):
    """Many-to-many relationship between User and Role"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    role = models.ForeignKey(Role, on_delete=models.CASCADE)
    assigned_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True,
        related_name='assigned_roles'
    )
    assigned_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'user_roles'
        unique_together = ['user', 'role']
        ordering = ['-assigned_at']
        verbose_name = 'User Role'
        verbose_name_plural = 'User Roles'

    def __str__(self):
        return f"{self.user.username} - {self.role.name}"


class UserActivityLog(models.Model):
    """Audit log for user activities"""
    ACTION_CHOICES = (
        ('LOGIN', 'Login'),
        ('LOGOUT', 'Logout'),
        ('CREATE', 'Create'),
        ('UPDATE', 'Update'),
        ('DELETE', 'Delete'),
        ('VIEW', 'View'),
        ('EXPORT', 'Export'),
        ('OTHER', 'Other'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    description = models.TextField()
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'user_activity_logs'
        ordering = ['-timestamp']
        verbose_name = 'User Activity Log'
        verbose_name_plural = 'User Activity Logs'

    def __str__(self):
        return f"{self.user.username} - {self.action} at {self.timestamp}"
