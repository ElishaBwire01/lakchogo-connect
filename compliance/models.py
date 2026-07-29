from django.db import models
from django.conf import settings
from django.utils import timezone
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
        default=75.00
    )
    grace_period_days = models.IntegerField(default=30)
    penalty_points = models.DecimalField(max_digits=5, decimal_places=2, default=10.00)
    is_active = models.BooleanField(default=True)
    order = models.IntegerField(default=0)
    
    class Meta:
        db_table = 'compliance_rules'
        ordering = ['order', 'name']
        verbose_name = 'Compliance Rule'
        verbose_name_plural = 'Compliance Rules'
    
    def __str__(self):
        return f"{self.name} ({self.get_rule_type_display()})"


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
    ALERT_TYPES = (
        ('payment_overdue', 'Payment Overdue'),
        ('attendance_low', 'Low Attendance'),
        ('compliance_low', 'Low Compliance Score'),
        ('status_changed', 'Status Changed'),
        ('warning_issued', 'Warning Issued'),
    )
    
    PRIORITY_CHOICES = (
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    )
    
    member = models.ForeignKey(
        Member,
        on_delete=models.CASCADE,
        related_name='compliance_alerts'
    )
    alert_type = models.CharField(max_length=30, choices=ALERT_TYPES)
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')
    message = models.TextField()
    is_resolved = models.BooleanField(default=False)
    resolved_at = models.DateTimeField(null=True, blank=True)
    resolved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='resolved_compliance_alerts'
    )
    resolution_notes = models.TextField(blank=True)
    
    class Meta:
        db_table = 'compliance_alerts'
        ordering = ['-created_at']
        verbose_name = 'Compliance Alert'
        verbose_name_plural = 'Compliance Alerts'
    
    def __str__(self):
        return f"{self.member.get_full_name()} - {self.get_alert_type_display()}"
    
    def resolve(self, user, notes=''):
        self.is_resolved = True
        self.resolved_at = timezone.now()
        self.resolved_by = user
        self.resolution_notes = notes
        self.save()


class ComplianceReport(BaseModel):
    """Generated compliance reports"""
    REPORT_TYPES = (
        ('summary', 'Summary Report'),
        ('detailed', 'Detailed Report'),
        ('members', 'Members Report'),
        ('warnings', 'Warnings Report'),
    )
    
    report_type = models.CharField(max_length=20, choices=REPORT_TYPES)
    generated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='compliance_reports'  # CHANGED: unique related_name
    )
    data = models.JSONField(default=dict)
    file = models.FileField(upload_to='compliance_reports/', null=True, blank=True)
    notes = models.TextField(blank=True)
    
    class Meta:
        db_table = 'compliance_reports'
        ordering = ['-created_at']
        verbose_name = 'Compliance Report'
        verbose_name_plural = 'Compliance Reports'
    
    def __str__(self):
        return f"{self.get_report_type_display()} - {self.created_at.strftime('%Y-%m-%d')}"
