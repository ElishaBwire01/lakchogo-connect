"""
Custom model managers for LakChogo Connect
Provides common query methods
"""

from django.db import models
from django.db.models import Q

class BaseManager(models.Manager):
    """Base manager with common query methods"""
    
    def get_queryset(self):
        return super().get_queryset()
    
    def active(self):
        """Get only active records"""
        return self.get_queryset().filter(is_active=True)
    
    def inactive(self):
        """Get only inactive records"""
        return self.get_queryset().filter(is_active=False)
    
    def search(self, query, fields=None):
        """
        Search across specified fields
        If no fields specified, searches common fields
        """
        if not query:
            return self.get_queryset()
        
        if not fields:
            # Try common search fields
            model = self.model
            fields = []
            
            # Common string fields
            possible_fields = ['name', 'title', 'description', 'notes']
            for field in possible_fields:
                if hasattr(model, field):
                    fields.append(field)
            
            # If no fields found, use first string field
            if not fields:
                for field in model._meta.fields:
                    if isinstance(field, (models.CharField, models.TextField)):
                        fields.append(field.name)
                        break
        
        q_objects = Q()
        for field in fields:
            q_objects |= Q(**{f'{field}__icontains': query})
        
        return self.get_queryset().filter(q_objects)
    
    def get_or_create_with_defaults(self, defaults=None, **kwargs):
        """Get or create with default values"""
        return self.get_queryset().get_or_create(defaults=defaults or {}, **kwargs)
    
    
class SoftDeleteManager(BaseManager):
    """Manager for soft-delete models"""
    
    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False)
    
    def deleted(self):
        """Get only deleted records"""
        return self.get_queryset().filter(is_deleted=True)
    
    def all_with_deleted(self):
        """Get all records including deleted"""
        return super().get_queryset()
