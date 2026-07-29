from django.contrib import admin
from .models import DashboardWidget, UserDashboardPreference, DashboardMetric

@admin.register(DashboardWidget)
class DashboardWidgetAdmin(admin.ModelAdmin):
    list_display = ('title', 'widget_type', 'position', 'order', 'is_active')
    list_filter = ('widget_type', 'position', 'is_active')
    search_fields = ('title', 'settings')
    ordering = ('position', 'order')

@admin.register(UserDashboardPreference)
class UserDashboardPreferenceAdmin(admin.ModelAdmin):
    list_display = ('user', 'theme', 'created_at')
    search_fields = ('user__username', 'theme')
    raw_id_fields = ('user',)
    filter_horizontal = ('widgets',)

@admin.register(DashboardMetric)
class DashboardMetricAdmin(admin.ModelAdmin):
    list_display = ('name', 'key', 'value', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name', 'key', 'value')
