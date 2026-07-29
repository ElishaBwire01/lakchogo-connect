from django.db import models
from django.utils import timezone

class BaseModel(models.Model):
    """Abstract base model with common fields"""
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        abstract = True
        ordering = ['-created_at']

    def soft_delete(self):
        self.is_active = False
        self.save()
