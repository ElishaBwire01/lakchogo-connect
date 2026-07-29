from django.db import models
from django.conf import settings
from django.utils import timezone
from core.models import BaseModel
from members.models import Member
from finance.models import PaymentCategory

class ComplianceRule(BaseModel):
    """Rules for compliance calculation"""
    RULE_TYPES = (
        ('payment', 'Payment'),
        ('attendance', 'Attendance'),
        ('combined', 'Combined'),
    )
    
    name = models.CharField(max_length=100, help_text="Name of the compliance rule")
    description = models.TextField(blank=True, help_text="Detailed description of the rule")
    rule_type = models.CharField(max_length=20, choices=RULE_TYPES, help_text="Type of compliance rule")
    target_category = models.ForeignKey(
        PaymentCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='compliance_rules',
        help_text="Payment category this rule applies to (if payment rule)"
    )
    min_attendance_percentage = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        default=75.00,
        help_text="Minimum attendance percentage required (for attendance rules)"
    )
    grace_period_days = models.IntegerField(
        default=30,
        help_text="Grace period in days before compliance is affected"
    )
    penalty_points = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=10.00,
        help_text="Points deducted for non-compliance"
    )
    is_active = models.BooleanField(default=True, help_text="Whether this rule is currently active")
    order = models.IntegerField(default=0, help_text="Order in which rules are applied")
    
    class Meta:
        db_table = 'compliance_rules'
        ordering = ['order', 'name']
        verbose_name = 'Compliance Rule'
        verbose_name_plural = 'Compliance Rules'
    
    def __str__(self):
        return f"{self.name} ({self.get_rule_type_display()})"
    
    def apply_rule(self, member):
        """Apply this rule to a member and return penalty points"""
        if not self.is_active:
            return 0
        
        if self.rule_type == 'payment':
            return self._check_payment_compliance(member)
        elif self.rule_type == 'attendance':
            return self._check_attendance_compliance(member)
        else:
            return (self._check_payment_compliance(member) + 
                   self._check_attendance_compliance(member)) / 2
    
    def _check_payment_compliance(self, member):
        """Check payment compliance for a member"""
        from finance.models import Payment
        
        # Get member's payments for this category
        payments = Payment.objects.filter(
            member=member,
            category=self.target_category,
            status='completed'
        )
        
        if not payments.exists():
            return self.penalty_points
        
        # Check if payment is within grace period
        last_payment = payments.order_by('-created_at').first()
        days_since_payment = (timezone.now().date() - last_payment.created_at.date()).days
        
        if days_since_payment > self.grace_period_days:
            return self.penalty_points
        
        return 0
    
    def _check_attendance_compliance(self, member):
        """Check attendance compliance for a member"""
        from meetings.models import Attendance
        from meetings.models import Meeting
        
        # Get member's meetings in last 3 months
        three_months_ago = timezone.now() - timezone.timedelta(days=90)
        meetings = Meeting.objects.filter(
            date__gte=three_months_ago,
            status='completed'
        )
        
        if not meetings.exists():
            return 0
        
        total_meetings = meetings.count()
        attended = Attendance.objects.filter(
            member=member,
            meeting__in=meetings,
            status='present'
        ).count()
        
        attendance_rate = (attended / total_meetings) * 100 if total_meetings > 0 else 0
        
        if attendance_rate < self.min_attendance_percentage:
            return self.penalty_points
        
        return 0


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
        related_name='compliance_score',
        help_text="Member this score belongs to"
    )
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='green',
        help_text="Current compliance status"
    )
    score = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        default=100.00,
        help_text="Overall compliance score (0-100)"
    )
    payment_compliance = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        default=100.00,
        help_text="Payment compliance score"
    )
    attendance_compliance = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        default=100.00,
        help_text="Attendance compliance score"
    )
    last_checked = models.DateTimeField(
        auto_now=True,
        help_text="Last time compliance was checked"
    )
    warnings = models.JSONField(
        default=list, 
        blank=True,
        help_text="List of active warnings"
    )
    history = models.JSONField(
        default=list, 
        blank=True,
        help_text="Historical compliance data"
    )
    
    class Meta:
        db_table = 'compliance_scores'
        ordering = ['-score']
        verbose_name = 'Compliance Score'
        verbose_name_plural = 'Compliance Scores'
    
    def __str__(self):
        return f"{self.member.get_full_name()} - {self.status} ({self.score}%)"
    
    def update_score(self, penalty=0):
        """Update compliance score based on penalties"""
        self.score = max(0, self.score - penalty)
        self.update_status()
        self.save()
    
    def update_status(self):
        """Update compliance status based on score"""
        if self.score >= 80:
            self.status = 'green'
        elif self.score >= 60:
            self.status = 'yellow'
        else:
            self.status = 'red'
        self.save()
    
    def add_warning(self, message):
        """Add a warning to the member"""
        if message not in self.warnings:
            self.warnings.append(message)
            self.save()
    
    def clear_warnings(self):
        """Clear all warnings"""
        self.warnings = []
        self.save()
    
    @property
    def is_eligible(self):
        return self.status == 'green'
    
    @property
    def is_warning(self):
        return self.status == 'yellow'
    
    @property
    def is_not_eligible(self):
        return self.status == 'red'
    
    def get_compliance_details(self):
        """Get detailed compliance information"""
        return {
            'member': self.member.get_full_name(),
            'member_id': self.member.member_id,
            'status': self.status,
            'score': self.score,
            'payment_score': self.payment_compliance,
            'attendance_score': self.attendance_compliance,
            'warnings': self.warnings,
            'last_checked': self.last_checked,
        }


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
        related_name='compliance_alerts',
        help_text="Member this alert is for"
    )
    alert_type = models.CharField(
        max_length=30, 
        choices=ALERT_TYPES,
        help_text="Type of alert"
    )
    priority = models.CharField(
        max_length=20, 
        choices=PRIORITY_CHOICES, 
        default='medium',
        help_text="Alert priority level"
    )
    message = models.TextField(help_text="Alert message")
    is_resolved = models.BooleanField(default=False, help_text="Whether the alert is resolved")
    resolved_at = models.DateTimeField(null=True, blank=True, help_text="When the alert was resolved")
    resolved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='resolved_alerts',
        help_text="User who resolved the alert"
    )
    resolution_notes = models.TextField(blank=True, help_text="Notes about resolution")
    
    class Meta:
        db_table = 'compliance_alerts'
        ordering = ['-created_at']
        verbose_name = 'Compliance Alert'
        verbose_name_plural = 'Compliance Alerts'
    
    def __str__(self):
        return f"{self.member.get_full_name()} - {self.get_alert_type_display()}"
    
    def resolve(self, user, notes=''):
        """Resolve the alert"""
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
        related_name='generated_reports'
    )
    data = models.JSONField(default=dict, help_text="Report data")
    file = models.FileField(upload_to='compliance_reports/', null=True, blank=True)
    notes = models.TextField(blank=True)
    
    class Meta:
        db_table = 'compliance_reports'
        ordering = ['-created_at']
        verbose_name = 'Compliance Report'
        verbose_name_plural = 'Compliance Reports'
    
    def __str__(self):
        return f"{self.get_report_type_display()} - {self.created_at.strftime('%Y-%m-%d')}"
