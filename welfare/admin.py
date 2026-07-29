from django.contrib import admin
from .models import BereavementEvent, BereavementContribution, WelfareFund, WelfareRequest

@admin.register(BereavementEvent)
class BereavementEventAdmin(admin.ModelAdmin):
    list_display = ('event_code', 'member', 'deceased_name', 'collection_target', 'amount_collected', 'status')
    list_filter = ('status', 'date_of_death', 'created_at')
    search_fields = ('event_code', 'deceased_name', 'member__user__first_name', 'member__user__last_name')
    raw_id_fields = ('member', 'approved_by')
    readonly_fields = ('event_code', 'amount_collected', 'created_at', 'updated_at')
    date_hierarchy = 'date_of_death'
    fieldsets = (
        ('Basic Information', {
            'fields': ('event_code', 'member', 'deceased_name', 'relationship', 'description')
        }),
        ('Dates', {
            'fields': ('date_of_death', 'date_of_burial')
        }),
        ('Financial', {
            'fields': ('collection_target', 'amount_collected', 'amount_disbursed')
        }),
        ('Status', {
            'fields': ('status', 'payout_date', 'disbursement_notes', 'approved_by', 'approved_at')
        }),
    )

@admin.register(BereavementContribution)
class BereavementContributionAdmin(admin.ModelAdmin):
    list_display = ('event', 'contributor', 'contributor_name', 'amount', 'contribution_type', 'created_at')
    list_filter = ('contribution_type', 'is_public_contribution', 'payment_method')
    search_fields = ('event__event_code', 'contributor__user__first_name', 'contributor_name')
    raw_id_fields = ('event', 'contributor', 'recorded_by')
    date_hierarchy = 'created_at'

@admin.register(WelfareFund)
class WelfareFundAdmin(admin.ModelAdmin):
    list_display = ('name', 'fund_type', 'balance', 'is_active')
    list_filter = ('fund_type', 'is_active')
    search_fields = ('name', 'description')
    raw_id_fields = ('created_by',)

@admin.register(WelfareRequest)
class WelfareRequestAdmin(admin.ModelAdmin):
    list_display = ('member', 'title', 'request_type', 'amount_requested', 'status', 'created_at')
    list_filter = ('status', 'request_type', 'created_at')
    search_fields = ('title', 'description', 'member__user__first_name', 'member__user__last_name')
    raw_id_fields = ('member', 'reviewed_by', 'approved_by', 'disbursed_by')
    date_hierarchy = 'created_at'
