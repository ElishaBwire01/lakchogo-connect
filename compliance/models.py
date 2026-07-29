from django.db import models
from django.conf import settings
from core.models import BaseModel
from members.models import Member

class ComplianceRule(BaseModel):
    """Rules for compliance calculation"""
    RULE_TYPES = (
        ('payment', 'Payment'),
        ('attendance', 'Attendance'),
        ('combined', 'Combined'),
    )
    
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    rule_type = models.CharField(max_length=20, choices=RULE_TYPES)
    target_category = models.ForeignKey(
        'finance.PaymentCategory',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='compliance_rules'
    )
    min_attendance_percentage = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        default=75.00,
        help_text="Minimum attendance percentage required"
    )
    grace_period_days = models.IntegerField(default=30)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'compliance_rules'
        ordering = ['name']
        verbose_name = 'Compliance Rule'
        verbose_name_plural = 'Compliance Rules'
    
    def __str__(self):
        return self.name


class ComplianceScore(BaseModel):
    """Compliance score for each member"""
    STATUS_CHOICES = (
        ('green', 'Eligible'),
        ('yellow', 'Warning'),
        ('red', 'Not Eligible'),
    )
    
    member = models.OneToOneField(
        Member,
        on_delete=models.CASCADE,
        related_name='compliance_score'
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='green')
    score = models.DecimalField(max_digits=5, decimal_places=2, default=100.00)
    payment_compliance = models.DecimalField(max_digits=5, decimal_places=2, default=100.00)
    attendance_compliance = models.DecimalField(max_digits=5, decimal_places=2, default=100.00)
    last_checked = models.DateTimeField(auto_now=True)
    warnings = models.JSONField(default=list, blank=True)
    
    class Meta:
        db_table = 'compliance_scores'
        ordering = ['-score']
        verbose_name = 'Compliance Score'
        verbose_name_plural = 'Compliance Scores'
    
    def __str__(self):
        return f"{self.member.get_full_name()} - {self.status}"
    
    def update_status(self):
        """Update compliance status based on score"""
        if self.score >= 80:
            self.status = 'green'
        elif self.score >= 60:
            self.status = 'yellow'
        else:
            self.status = 'red'
        self.save()
    
    @property
    def is_eligible(self):
        return self.status == 'green'


class ComplianceAlert(BaseModel):
    """Alerts for compliance issues"""
    member = models.ForeignKey(
        Member,
        on_delete=models.CASCADE,
        related_name='compliance_alerts'
    )
    message = models.TextField()
    is_resolved = models.BooleanField(default=False)
    resolved_at = models.DateTimeField(null=True, blank=True)
    resolved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    
    class Meta:
        db_table = 'compliance_alerts'
        ordering = ['-created_at']
        verbose_name = 'Compliance Alert'
        verbose_name_plural = 'Compliance Alerts'
    
    def __str__(self):
        return f"Alert for {self.member.get_full_name()}: {self.message[:50]}"
    
    def resolve(self, user):
        self.is_resolved = True
        self.resolved_at = models.DateTimeField(auto_now=True)
        self.resolved_by = user
        self.save()
