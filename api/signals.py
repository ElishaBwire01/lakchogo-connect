# API Signals
# This file is for API-related signal handlers
# Currently empty - can be extended for API-specific functionality

from django.db.models.signals import post_save
from django.dispatch import receiver

# Add any API-specific signals here if needed
# For example:
# @receiver(post_save, sender=User)
# def api_user_saved(sender, instance, created, **kwargs):
#     pass
