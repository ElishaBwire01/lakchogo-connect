"""
Core signals for LakChogo Connect
"""

from django.db.models.signals import pre_save, post_save, pre_delete, post_delete
from django.dispatch import receiver
from django.contrib.auth import get_user_model

User = get_user_model()

@receiver(pre_save)
def set_updated_by(sender, instance, **kwargs):
    """
    Automatically set updated_by field if available
    """
    if hasattr(instance, 'updated_by') and hasattr(instance, '_request'):
        if instance._request and instance._request.user.is_authenticated:
            instance.updated_by = instance._request.user


@receiver(post_save)
def post_save_handler(sender, instance, created, **kwargs):
    """
    Generic post-save handler for logging
    """
    if created:
        # Log creation
        print(f"[CREATED] {sender.__name__}: {instance}")
    else:
        # Log update
        print(f"[UPDATED] {sender.__name__}: {instance}")


@receiver(pre_delete)
def pre_delete_handler(sender, instance, **kwargs):
    """
    Generic pre-delete handler for logging
    """
    print(f"[DELETING] {sender.__name__}: {instance}")


@receiver(post_delete)
def post_delete_handler(sender, instance, **kwargs):
    """
    Generic post-delete handler for logging
    """
    print(f"[DELETED] {sender.__name__}: {instance}")
