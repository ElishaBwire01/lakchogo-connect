from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import UserActivityLog

User = get_user_model()

@receiver(post_save, sender=User)
def log_user_creation(sender, instance, created, **kwargs):
    """Log when a user is created or updated"""
    if created:
        UserActivityLog.objects.create(
            user=instance,
            action='CREATE',
            description=f'User account created: {instance.get_full_name()}'
        )

@receiver(pre_delete, sender=User)
def log_user_deletion(sender, instance, **kwargs):
    """Log when a user is deleted"""
    UserActivityLog.objects.create(
        user=instance,
        action='DELETE',
        description=f'User account deleted: {instance.get_full_name()}'
    )
