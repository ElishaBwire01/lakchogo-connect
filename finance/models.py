from django.db import models
from django.conf import settings
from django.utils import timezone
from core.models import BaseModel
from members.models import Member

class PaymentCategory(BaseModel):
    """Payment categories like Yearly Subscription, Emergency Fund, etc."""
    FREQUENCY_CHOICES = (
        ('monthly', 'Monthly'),
        ('yearly', 'Yearly'),
        ('one-time', 'One-Time'),
        ('quarterly', 'Quarterly'),
        ('weekly', 'Weekly'),
    )
    
    name = models.CharField(max_length=100, help_text="Name of the payment category")
    description = models.TextField(blank=True, help_text="Detailed description")
    default_amount = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0,
        help_text="Default amount for this category"
    )
    frequency = models.CharField(
        max_length=20, 
        choices=FREQUENCY_CHOICES, 
        default='one-time',
        help_text="How often this payment is required"
    )
    is_mandatory_for_welfare = models.BooleanField(
        default=False,
        help_text="Whether this payment is required for welfare eligibility"
    )
    is_active = models.BooleanField(default=True, help_text="Whether this category is active")
    color = models.CharField(
        max_length=20, 
        default='primary',
        help_text="Color for displaying this category"
    )
    icon = models.CharField(
        max_length=50, 
        default='fa-money-bill',
        help_text="Font Awesome icon class"
    )
    order = models.IntegerField(default=0, help_text="Display order")
    
    class Meta:
        db_table = 'payment_categories'
        ordering = ['order', 'name']
        verbose_name = 'Payment Category'
        verbose_name_plural = 'Payment Categories'
    
    def __str__(self):
        return f"{self.name} (KES {self.default_amount})"
    
    def get_color_class(self):
        color_map = {
            'primary': 'bg-primary',
            'success': 'bg-success',
            'warning': 'bg-warning',
            'danger': 'bg-danger',
            'info': 'bg-info',
            'secondary': 'bg-secondary',
        }
        return color_map.get(self.color, 'bg-primary')


class Payment(BaseModel):
    """Payment records for members"""
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
        ('cancelled', 'Cancelled'),
    )
    
    PAYMENT_METHODS = (
        ('mpesa', 'M-Pesa'),
        ('airtel', 'Airtel Money'),
        ('cash', 'Cash'),
        ('bank', 'Bank Transfer'),
        ('cheque', 'Cheque'),
        ('other', 'Other'),
    )
    
    member = models.ForeignKey(
        Member,
        on_delete=models.CASCADE,
        related_name='payments',
        help_text="Member making the payment"
    )
    category = models.ForeignKey(
        PaymentCategory,
        on_delete=models.CASCADE,
        related_name='payments',
        help_text="Payment category"
    )
    amount = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        help_text="Payment amount"
    )
    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_METHODS,
        default='cash',
        help_text="How the payment was made"
    )
    transaction_ref = models.CharField(
        max_length=50,
        blank=True,
        help_text="Transaction reference number"
    )
    external_ref = models.CharField(
        max_length=50,
        blank=True,
        help_text="External reference (M-Pesa code, etc.)"
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        help_text="Payment status"
    )
    recorded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='recorded_payments',
        help_text="User who recorded the payment"
    )
    verified_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='verified_payments',
        help_text="User who verified the payment"
    )
    verified_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When the payment was verified"
    )
    receipt_url = models.URLField(
        blank=True,
        help_text="URL to digital receipt"
    )
    receipt_file = models.FileField(
        upload_to='receipts/',
        null=True,
        blank=True,
        help_text="Uploaded receipt file"
    )
    notes = models.TextField(blank=True, help_text="Additional notes")
    
    class Meta:
        db_table = 'payments'
        ordering = ['-created_at']
        verbose_name = 'Payment'
        verbose_name_plural = 'Payments'
    
    def __str__(self):
        return f"{self.member.get_full_name()} - {self.category.name} - KES {self.amount}"
    
    def verify(self, user):
        """Verify a pending payment"""
        self.status = 'completed'
        self.verified_by = user
        self.verified_at = timezone.now()
        self.save()
    
    def cancel(self):
        """Cancel a payment"""
        self.status = 'cancelled'
        self.save()
    
    def refund(self):
        """Refund a payment"""
        self.status = 'refunded'
        self.save()
    
    @property
    def is_pending(self):
        return self.status == 'pending'
    
    @property
    def is_completed(self):
        return self.status == 'completed'


class PaymentReceipt(BaseModel):
    """Digital receipts for payments"""
    payment = models.OneToOneField(
        Payment,
        on_delete=models.CASCADE,
        related_name='receipt'
    )
    receipt_number = models.CharField(
        max_length=20,
        unique=True,
        help_text="Unique receipt number"
    )
    generated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='generated_receipts'
    )
    generated_at = models.DateTimeField(auto_now_add=True)
    pdf_file = models.FileField(
        upload_to='receipts/pdf/',
        null=True,
        blank=True
    )
    html_content = models.TextField(blank=True)
    
    class Meta:
        db_table = 'payment_receipts'
        ordering = ['-generated_at']
        verbose_name = 'Payment Receipt'
        verbose_name_plural = 'Payment Receipts'
    
    def __str__(self):
        return f"Receipt #{self.receipt_number} - {self.payment.member.get_full_name()}"


class PaymentReminder(BaseModel):
    """Payment reminders sent to members"""
    REMINDER_TYPES = (
        ('overdue', 'Overdue'),
        ('upcoming', 'Upcoming'),
        ('manual', 'Manual'),
    )
    
    member = models.ForeignKey(
        Member,
        on_delete=models.CASCADE,
        related_name='payment_reminders'
    )
    category = models.ForeignKey(
        PaymentCategory,
        on_delete=models.CASCADE,
        related_name='reminders',
        null=True,
        blank=True
    )
    reminder_type = models.CharField(max_length=20, choices=REMINDER_TYPES)
    message = models.TextField()
    sent_at = models.DateTimeField(auto_now_add=True)
    sent_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='sent_reminders'
    )
    is_read = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'payment_reminders'
        ordering = ['-sent_at']
        verbose_name = 'Payment Reminder'
        verbose_name_plural = 'Payment Reminders'
    
    def __str__(self):
        return f"Reminder for {self.member.get_full_name()} - {self.reminder_type}"


class PaymentReport(BaseModel):
    """Saved payment reports"""
    REPORT_TYPES = (
        ('summary', 'Summary Report'),
        ('detailed', 'Detailed Report'),
        ('member', 'Member Report'),
        ('category', 'Category Report'),
        ('period', 'Period Report'),
    )
    
    report_type = models.CharField(max_length=20, choices=REPORT_TYPES)
    generated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='payment_reports'
    )
    filters = models.JSONField(default=dict, blank=True)
    data = models.JSONField(default=dict)
    file = models.FileField(upload_to='reports/payments/', null=True, blank=True)
    notes = models.TextField(blank=True)
    
    class Meta:
        db_table = 'payment_reports'
        ordering = ['-created_at']
        verbose_name = 'Payment Report'
        verbose_name_plural = 'Payment Reports'
    
    def __str__(self):
        return f"{self.get_report_type_display()} - {self.created_at.strftime('%Y-%m-%d')}"
