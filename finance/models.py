from django.db import models
from django.conf import settings
from core.models import BaseModel
from members.models import Member

class PaymentCategory(BaseModel):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    default_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    frequency = models.CharField(max_length=20, choices=(
        ('monthly', 'Monthly'),
        ('yearly', 'Yearly'),
        ('one-time', 'One-Time'),
    ), default='one-time')
    is_mandatory_for_welfare = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'payment_categories'
        ordering = ['name']
        verbose_name = 'Payment Category'
        verbose_name_plural = 'Payment Categories'
    
    def __str__(self):
        return self.name


class Payment(BaseModel):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    )
    
    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='payments')
    category = models.ForeignKey(PaymentCategory, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=20, choices=(
        ('mpesa', 'M-Pesa'),
        ('airtel', 'Airtel Money'),
        ('cash', 'Cash'),
        ('bank', 'Bank Transfer'),
    ))
    transaction_ref = models.CharField(max_length=50, blank=True)
    external_ref = models.CharField(max_length=50, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    recorded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    receipt_url = models.URLField(blank=True)
    notes = models.TextField(blank=True)
    
    class Meta:
        db_table = 'payments'
        ordering = ['-created_at']
        verbose_name = 'Payment'
        verbose_name_plural = 'Payments'
    
    def __str__(self):
        return f"{self.member.get_full_name()} - {self.category.name} - KES {self.amount}"
