from django.contrib import admin
from .models import Report, ReportSchedule, ReportTemplate

@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ('title', 'report_type', 'generated_by', 'status', 'created_at')
    list_filter = ('report_type', 'status', 'created_at')
    search_fields = ('title', 'description', 'generated_by__username')
    raw_id_fields = ('generated_by',)
    readonly_fields = ('created_at', 'updated_at', 'generated_at', 'completed_at')

@admin.register(ReportSchedule)
class ReportScheduleAdmin(admin.ModelAdmin):
    list_display = ('report_type', 'schedule_type', 'is_active', 'last_run', 'next_run')
    list_filter = ('report_type', 'schedule_type', 'is_active')
    search_fields = ('report_type',)
    filter_horizontal = ('recipients',)

@admin.register(ReportTemplate)
class ReportTemplateAdmin(admin.ModelAdmin):
    list_display = ('name', 'report_type', 'is_default', 'is_active', 'created_by')
    list_filter = ('report_type', 'is_default', 'is_active')
    search_fields = ('name', 'description')
    raw_id_fields = ('created_by',)
