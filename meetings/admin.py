from django.contrib import admin
from .models import Meeting, Attendance, MeetingMinutes

@admin.register(Meeting)
class MeetingAdmin(admin.ModelAdmin):
    list_display = ('title', 'date', 'venue', 'status', 'created_by', 'created_at')
    list_filter = ('status', 'date', 'created_at')
    search_fields = ('title', 'venue', 'description', 'agenda')
    date_hierarchy = 'date'
    raw_id_fields = ('created_by',)
    readonly_fields = ('qr_code', 'created_at', 'updated_at')
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'description', 'status')
        }),
        ('Meeting Details', {
            'fields': ('date', 'venue', 'agenda')
        }),
        ('Minutes', {
            'fields': ('minutes_text', 'minutes_url')
        }),
        ('Metadata', {
            'fields': ('created_by', 'qr_code', 'created_at', 'updated_at')
        }),
    )

@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('member', 'meeting', 'status', 'check_in_method', 'check_in_time')
    list_filter = ('status', 'check_in_method', 'created_at')
    search_fields = ('member__user__first_name', 'member__user__last_name', 'meeting__title')
    raw_id_fields = ('member', 'meeting', 'recorded_by')
    readonly_fields = ('created_at', 'updated_at')

@admin.register(MeetingMinutes)
class MeetingMinutesAdmin(admin.ModelAdmin):
    list_display = ('meeting', 'attendees_count', 'created_at', 'approved_at')
    list_filter = ('created_at', 'approved_at')
    search_fields = ('meeting__title', 'content', 'summary')
    raw_id_fields = ('meeting', 'approved_by')
    readonly_fields = ('created_at', 'updated_at')
