from django.contrib import admin
from .models import ComplianceRule, ComplianceScore, ComplianceAlert, ComplianceReport

@admin.register(ComplianceRule)
class ComplianceRuleAdmin(admin.ModelAdmin):
    list_display = ('name', 'rule_type', 'penalty_points', 'is_active', 'order')
    list_filter = ('rule_type', 'is_active')
    search_fields = ('name', 'description')
    ordering = ('order',)

@admin.register(ComplianceScore)
class ComplianceScoreAdmin(admin.ModelAdmin):
    list_display = ('member', 'status', 'score', 'last_checked')
    list_filter = ('status', 'last_checked')
    search_fields = ('member__user__first_name', 'member__user__last_name')
    raw_id_fields = ('member',)
    readonly_fields = ('last_checked',)

@admin.register(ComplianceAlert)
class ComplianceAlertAdmin(admin.ModelAdmin):
    list_display = ('member', 'alert_type', 'priority', 'is_resolved', 'created_at')
    list_filter = ('alert_type', 'priority', 'is_resolved')
    search_fields = ('member__user__first_name', 'message')
    raw_id_fields = ('member', 'resolved_by')

@admin.register(ComplianceReport)
class ComplianceReportAdmin(admin.ModelAdmin):
    list_display = ('report_type', 'generated_by', 'created_at')
    list_filter = ('report_type', 'created_at')
    search_fields = ('generated_by__username',)
