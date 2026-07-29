"""
LakChogo Connect - Welfare Group Management System

This is the main package for the LakChogo Connect Django project.
"""

__version__ = '1.0.0'
__author__ = 'Lak Chogo Welfare Group'
__description__ = 'Digital platform for welfare group management'

# This will make sure the app is always imported when
# Django starts so that shared_task will use this app.
from .celery import app as celery_app

__all__ = ('celery_app',)
