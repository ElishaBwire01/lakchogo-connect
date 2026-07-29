from django.db import models
from django.conf import settings
from core.models import BaseModel

class DashboardWidget(BaseModel):
    """Widgets that appear on the dashboard"""
    WIDGET_TYPES = (
        ('stats', 'Statistics'),
        ('chart', 'Chart'),
        ('table', 'Table'),
        ('calendar', 'Calendar'),
        ('recent', 'Recent Activity'),
        ('custom', 'Custom'),
    )
    
    POSITIONS = (
        ('top', 'Top'),
        ('middle', 'Middle'),
        ('bottom', 'Bottom'),
    )
    
    title = models.CharField(max_length=100)
    widget_type = models.CharField(max_length=20, choices=WIDGET_TYPES)
    position = models.CharField(max_length=20, choices=POSITIONS, default='middle')
    order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    roles = models.JSONField(default=list, blank=True, help_text="Roles that can see this widget")
    settings = models.JSONField(default=dict, blank=True)
    
    class Meta:
        db_table = 'dashboard_widgets'
        ordering = ['position', 'order']
        verbose_name = 'Dashboard Widget'
        verbose_name_plural = 'Dashboard Widgets'
    
    def __str__(self):
        return self.title


class UserDashboardPreference(BaseModel):
    """User-specific dashboard preferences"""
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='dashboard_preferences'
    )
    layout = models.JSONField(default=dict, blank=True)
    widgets = models.ManyToManyField(DashboardWidget, blank=True)
    theme = models.CharField(max_length=20, default='default')
    
    class Meta:
        db_table = 'user_dashboard_preferences'
        verbose_name = 'User Dashboard Preference'
        verbose_name_plural = 'User Dashboard Preferences'
    
    def __str__(self):
        return f"{self.user.username}'s Preferences"


class DashboardMetric(BaseModel):
    """Metrics displayed on the dashboard"""
    name = models.CharField(max_length=100)
    key = models.CharField(max_length=50, unique=True)
    value = models.CharField(max_length=255)
    icon = models.CharField(max_length=50, blank=True)
    color = models.CharField(max_length=20, default='primary')
    is_active = models.BooleanField(default=True)
    roles = models.JSONField(default=list, blank=True)
    
    class Meta:
        db_table = 'dashboard_metrics'
        ordering = ['name']
        verbose_name = 'Dashboard Metric'
        verbose_name_plural = 'Dashboard Metrics'
    
    def __str__(self):
        return f"{self.name}: {self.value}"
