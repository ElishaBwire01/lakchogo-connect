from django.contrib import admin
from .models import ComplianceRule, ComplianceScore, ComplianceAlert

@admin.register(ComplianceRule)
class ComplianceRuleAdmin(admin.ModelAdmin):
    list_display = ('name', 'rule_type', 'min_attendance_percentage', 'grace_period_days', 'is_active')
    list_filter = ('rule_type', 'is_active')
    search_fields = ('name', 'description')

@admin.register(ComplianceScore)
class ComplianceScoreAdmin(admin.ModelAdmin):
    list_display = ('member', 'status', 'score', 'last_checked')
    list_filter = ('status', 'last_checked')
    search_fields = ('member__user__first_name', 'member__user__last_name', 'member__member_id')
    raw_id_fields = ('member',)
    readonly_fields = ('last_checked',)

@admin.register(ComplianceAlert)
class ComplianceAlertAdmin(admin.ModelAdmin):
    list_display = ('member', 'message_preview', 'is_resolved', 'created_at')
    list_filter = ('is_resolved', 'created_at')
    search_fields = ('member__user__first_name', 'member__user__last_name', 'message')
    raw_id_fields = ('member', 'resolved_by')
    
    def message_preview(self, obj):
        return obj.message[:50] + '...' if len(obj.message) > 50 else obj.message
    message_preview.short_description = 'Message'
