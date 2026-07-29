from django.contrib import admin
from .models import Member, MemberNote, MemberDocument, MemberContributionSummary

@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    list_display = ('member_id', 'get_full_name', 'status', 'compliance_status', 'date_joined')
    list_filter = ('status', 'compliance_status', 'date_joined', 'gender')
    search_fields = ('member_id', 'user__username', 'user__first_name', 'user__last_name', 'user__phone')
    raw_id_fields = ('user',)
    readonly_fields = ('member_id', 'date_joined')
    fieldsets = (
        ('Basic Information', {
            'fields': ('member_id', 'user', 'status', 'date_joined')
        }),
        ('Personal Information', {
            'fields': ('date_of_birth', 'gender', 'occupation', 'address')
        }),
        ('Next of Kin', {
            'fields': ('next_of_kin_name', 'next_of_kin_phone', 'next_of_kin_relationship', 'next_of_kin_address')
        }),
        ('Emergency Contact', {
            'fields': ('emergency_contact_name', 'emergency_contact_phone', 'emergency_contact_relationship')
        }),
        ('Compliance', {
            'fields': ('compliance_status',)
        }),
        ('Notes', {
            'fields': ('member_notes',)  # CHANGED: notes to member_notes
        }),
    )
    
    def get_full_name(self, obj):
        return obj.get_full_name()
    get_full_name.short_description = 'Full Name'

@admin.register(MemberNote)
class MemberNoteAdmin(admin.ModelAdmin):
    list_display = ('member', 'author', 'created_at', 'is_private')
    list_filter = ('is_private', 'created_at')
    search_fields = ('member__user__first_name', 'content')
    raw_id_fields = ('member', 'author')

@admin.register(MemberDocument)
class MemberDocumentAdmin(admin.ModelAdmin):
    list_display = ('member', 'document_type', 'title', 'uploaded_by', 'created_at')
    list_filter = ('document_type', 'created_at')
    search_fields = ('title', 'member__user__first_name')
    raw_id_fields = ('member', 'uploaded_by')

@admin.register(MemberContributionSummary)
class MemberContributionSummaryAdmin(admin.ModelAdmin):
    list_display = ('member', 'total_paid', 'total_expected', 'balance', 'attendance_rate')
    search_fields = ('member__user__first_name',)
    raw_id_fields = ('member',)
    readonly_fields = ('updated_at',)
