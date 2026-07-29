from django.contrib import admin
from .models import PaymentCategory, Payment, PaymentReceipt, PaymentReminder, PaymentReport

@admin.register(PaymentCategory)
class PaymentCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'default_amount', 'frequency', 'is_mandatory_for_welfare', 'is_active')
    list_filter = ('frequency', 'is_mandatory_for_welfare', 'is_active')
    search_fields = ('name', 'description')
    ordering = ('order',)

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('member', 'category', 'amount', 'payment_method', 'status', 'created_at')
    list_filter = ('status', 'payment_method', 'created_at')
    search_fields = ('member__user__first_name', 'member__user__last_name', 'transaction_ref')
    raw_id_fields = ('member', 'category', 'recorded_by', 'verified_by')
    date_hierarchy = 'created_at'
    readonly_fields = ('verified_at', 'created_at', 'updated_at')
    fieldsets = (
        ('Member Information', {
            'fields': ('member', 'category')
        }),
        ('Payment Details', {
            'fields': ('amount', 'payment_method', 'transaction_ref', 'external_ref')
        }),
        ('Status', {
            'fields': ('status', 'recorded_by', 'verified_by', 'verified_at')
        }),
        ('Additional', {
            'fields': ('receipt_url', 'receipt_file', 'notes')
        }),
    )

@admin.register(PaymentReceipt)
class PaymentReceiptAdmin(admin.ModelAdmin):
    list_display = ('receipt_number', 'payment', 'generated_at')
    search_fields = ('receipt_number', 'payment__member__user__first_name')
    raw_id_fields = ('payment', 'generated_by')

@admin.register(PaymentReminder)
class PaymentReminderAdmin(admin.ModelAdmin):
    list_display = ('member', 'reminder_type', 'sent_at', 'is_read')
    list_filter = ('reminder_type', 'is_read', 'sent_at')
    search_fields = ('member__user__first_name', 'message')
    raw_id_fields = ('member', 'category', 'sent_by')

@admin.register(PaymentReport)
class PaymentReportAdmin(admin.ModelAdmin):
    list_display = ('report_type', 'generated_by', 'created_at')
    list_filter = ('report_type', 'created_at')
    search_fields = ('generated_by__username',)
