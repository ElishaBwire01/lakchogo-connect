from django.db import models
from django.conf import settings
from core.models import BaseModel
from core.constants import REPORT_TYPE_CHOICES

class Report(BaseModel):
    """Generated reports"""
    REPORT_STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('generating', 'Generating'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    )
    
    report_type = models.CharField(max_length=20, choices=REPORT_TYPE_CHOICES)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    generated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='generated_reports'
    )
    status = models.CharField(max_length=20, choices=REPORT_STATUS_CHOICES, default='pending')
    file = models.FileField(upload_to='reports/', null=True, blank=True)
    file_url = models.URLField(blank=True)
    data = models.JSONField(default=dict, blank=True)
    filters = models.JSONField(default=dict, blank=True)
    notes = models.TextField(blank=True)
    generated_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'reports'
        ordering = ['-created_at']
        verbose_name = 'Report'
        verbose_name_plural = 'Reports'
    
    def __str__(self):
        return f"{self.get_report_type_display()} - {self.created_at.strftime('%Y-%m-%d')}"
    
    def mark_generating(self):
        self.status = 'generating'
        self.save()
    
    def mark_completed(self):
        from django.utils import timezone
        self.status = 'completed'
        self.completed_at = timezone.now()
        self.save()
    
    def mark_failed(self, error_message=''):
        self.status = 'failed'
        self.notes = error_message
        self.save()


class ReportSchedule(BaseModel):
    """Scheduled report generation"""
    SCHEDULE_TYPES = (
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
        ('yearly', 'Yearly'),
    )
    
    report_type = models.CharField(max_length=20, choices=REPORT_TYPE_CHOICES)
    schedule_type = models.CharField(max_length=20, choices=SCHEDULE_TYPES)
    recipients = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='scheduled_reports',
        blank=True
    )
    is_active = models.BooleanField(default=True)
    last_run = models.DateTimeField(null=True, blank=True)
    next_run = models.DateTimeField(null=True, blank=True)
    filters = models.JSONField(default=dict, blank=True)
    format = models.CharField(max_length=10, default='pdf', choices=(
        ('pdf', 'PDF'),
        ('csv', 'CSV'),
        ('excel', 'Excel'),
    ))
    
    class Meta:
        db_table = 'report_schedules'
        ordering = ['-created_at']
        verbose_name = 'Report Schedule'
        verbose_name_plural = 'Report Schedules'
    
    def __str__(self):
        return f"{self.get_report_type_display()} - {self.get_schedule_type_display()}"


class ReportTemplate(BaseModel):
    """Templates for reports"""
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    report_type = models.CharField(max_length=20, choices=REPORT_TYPE_CHOICES)
    template_html = models.TextField()
    css = models.TextField(blank=True)
    is_default = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='report_templates'
    )
    
    class Meta:
        db_table = 'report_templates'
        ordering = ['name']
        verbose_name = 'Report Template'
        verbose_name_plural = 'Report Templates'
    
    def __str__(self):
        return self.name
    
    def set_as_default(self):
        ReportTemplate.objects.filter(
            report_type=self.report_type,
            is_default=True
        ).update(is_default=False)
        self.is_default = True
        self.save()
