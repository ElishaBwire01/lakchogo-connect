"""
Base models for LakChogo Connect
Provides abstract base classes used by all apps
"""

from django.db import models
from django.utils import timezone

class BaseModel(models.Model):
    """
    Abstract base model with common fields
    All models in the application should inherit from this
    """
    
    created_at = models.DateTimeField(
        default=timezone.now,
        help_text="Date and time when the record was created"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Date and time when the record was last updated"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this record is active"
    )
    created_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='%(class)s_created',
        help_text="User who created this record"
    )
    updated_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='%(class)s_updated',
        help_text="User who last updated this record"
    )

    class Meta:
        abstract = True
        ordering = ['-created_at']

    def soft_delete(self):
        """Soft delete the record (set is_active=False)"""
        self.is_active = False
        self.save()
    
    def restore(self):
        """Restore a soft-deleted record"""
        self.is_active = True
        self.save()
    
    def save(self, *args, **kwargs):
        """Override save to auto-populate updated_at"""
        self.updated_at = timezone.now()
        super().save(*args, **kwargs)


class AuditLogModel(models.Model):
    """
    Abstract model for audit logging
    Tracks who created and modified records
    """
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='%(class)s_created_by'
    )
    updated_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='%(class)s_updated_by'
    )

    class Meta:
        abstract = True


class SoftDeleteModel(models.Model):
    """
    Abstract model for soft delete functionality
    """
    
    deleted_at = models.DateTimeField(null=True, blank=True)
    deleted_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='%(class)s_deleted_by'
    )
    is_deleted = models.BooleanField(default=False)

    class Meta:
        abstract = True

    def delete(self, using=None, keep_parents=False):
        """Soft delete instead of hard delete"""
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.save()
    
    def hard_delete(self):
        """Permanently delete the record"""
        super().delete()
    
    def restore(self):
        """Restore a soft-deleted record"""
        self.is_deleted = False
        self.deleted_at = None
        self.save()


class TimeStampedModel(models.Model):
    """
    Abstract model with timestamp fields only
    """
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
