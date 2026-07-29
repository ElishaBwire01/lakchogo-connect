from django.db import models
from django.conf import settings
from django.utils import timezone
from core.models import BaseModel
from core.constants import COMPLIANCE_STATUS_CHOICES

class Member(BaseModel):
    """Member model for LakChogo Welfare Group"""
    STATUS_CHOICES = (
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('suspended', 'Suspended'),
        ('pending', 'Pending'),
    )
    
    member_id = models.CharField(
        max_length=20, 
        unique=True, 
        blank=True,
        help_text="Auto-generated member ID (e.g., LCG-0001)"
    )
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='member',
        help_text="User account associated with this member"
    )
    
    # Personal Information
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(
        max_length=20, 
        blank=True,
        choices=(
            ('male', 'Male'),
            ('female', 'Female'),
            ('other', 'Other'),
        )
    )
    occupation = models.CharField(max_length=100, blank=True)
    address = models.TextField(blank=True)
    
    # Next of Kin
    next_of_kin_name = models.CharField(max_length=100, blank=True)
    next_of_kin_phone = models.CharField(max_length=17, blank=True)
    next_of_kin_relationship = models.CharField(max_length=50, blank=True)
    next_of_kin_address = models.TextField(blank=True)
    
    # Membership Details
    date_joined = models.DateTimeField(default=timezone.now)
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='pending',
        help_text="Member status"
    )
    compliance_status = models.CharField(
        max_length=20, 
        choices=COMPLIANCE_STATUS_CHOICES, 
        default='green',
        help_text="Current compliance status"
    )
    
    # Additional Information
    notes = models.TextField(blank=True, help_text="Additional notes about the member")  # Back to 'notes'
    emergency_contact_name = models.CharField(max_length=100, blank=True)
    emergency_contact_phone = models.CharField(max_length=17, blank=True)
    emergency_contact_relationship = models.CharField(max_length=50, blank=True)
    
    class Meta:
        db_table = 'members'
        ordering = ['-date_joined']
        verbose_name = 'Member'
        verbose_name_plural = 'Members'
    
    def __str__(self):
        return f"{self.member_id} - {self.user.get_full_name()}"
    
    def get_full_name(self):
        return self.user.get_full_name()
    
    def save(self, *args, **kwargs):
        if not self.member_id:
            # Generate member ID: LCG-XXXX
            last_member = Member.objects.order_by('-id').first()
            if last_member and last_member.member_id:
                try:
                    last_id = int(last_member.member_id.split('-')[1])
                    new_id = last_id + 1
                except (IndexError, ValueError):
                    new_id = 1
            else:
                new_id = 1
            self.member_id = f"LCG-{str(new_id).zfill(4)}"
        super().save(*args, **kwargs)
    
    @property
    def is_active(self):
        return self.status == 'active'
    
    @property
    def is_eligible(self):
        return self.compliance_status == 'green'
    
    @property
    def is_pending(self):
        return self.status == 'pending'
    
    def activate(self):
        """Activate a pending member"""
        self.status = 'active'
        self.save()
    
    def suspend(self):
        """Suspend a member"""
        self.status = 'suspended'
        self.save()
    
    def deactivate(self):
        """Deactivate a member"""
        self.status = 'inactive'
        self.save()


class MemberNote(BaseModel):
    """Notes about members"""
    member = models.ForeignKey(
        Member,
        on_delete=models.CASCADE,
        related_name='member_notes_list',  # Different related_name
        help_text="Member this note belongs to"
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='authored_member_notes'
    )
    content = models.TextField()
    is_private = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'member_notes'
        ordering = ['-created_at']
        verbose_name = 'Member Note'
        verbose_name_plural = 'Member Notes'
    
    def __str__(self):
        return f"Note for {self.member.get_full_name()} - {self.created_at.strftime('%Y-%m-%d')}"


class MemberDocument(BaseModel):
    """Documents uploaded for members"""
    DOCUMENT_TYPES = (
        ('id', 'ID Card'),
        ('passport', 'Passport'),
        ('photo', 'Photo'),
        ('certificate', 'Certificate'),
        ('other', 'Other'),
    )
    
    member = models.ForeignKey(
        Member,
        on_delete=models.CASCADE,
        related_name='documents'
    )
    document_type = models.CharField(max_length=20, choices=DOCUMENT_TYPES)
    title = models.CharField(max_length=100)
    file = models.FileField(upload_to='member_documents/')
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='uploaded_documents'
    )
    description = models.TextField(blank=True)
    
    class Meta:
        db_table = 'member_documents'
        ordering = ['-created_at']
        verbose_name = 'Member Document'
        verbose_name_plural = 'Member Documents'
    
    def __str__(self):
        return f"{self.member.get_full_name()} - {self.title}"


class MemberContributionSummary(BaseModel):
    """Summary of member contributions"""
    member = models.OneToOneField(
        Member,
        on_delete=models.CASCADE,
        related_name='contribution_summary'
    )
    total_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_expected = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    last_payment_date = models.DateTimeField(null=True, blank=True)
    total_meetings_attended = models.IntegerField(default=0)
    total_meetings = models.IntegerField(default=0)
    attendance_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'member_contribution_summaries'
        verbose_name = 'Member Contribution Summary'
        verbose_name_plural = 'Member Contribution Summaries'
    
    def __str__(self):
        return f"{self.member.get_full_name()} - Balance: KES {self.balance}"
    
    def update_summary(self):
        """Update the contribution summary"""
        from finance.models import Payment
        from meetings.models import Attendance, Meeting
        
        # Calculate payments
        payments = Payment.objects.filter(
            member=self.member,
            status='completed'
        )
        self.total_paid = payments.aggregate(models.Sum('amount'))['amount__sum'] or 0
        
        # Calculate expected (based on categories)
        from finance.models import PaymentCategory
        categories = PaymentCategory.objects.filter(is_active=True)
        self.total_expected = sum([cat.default_amount for cat in categories])
        
        self.balance = self.total_expected - self.total_paid
        
        # Get last payment date
        last_payment = payments.order_by('-created_at').first()
        self.last_payment_date = last_payment.created_at if last_payment else None
        
        # Calculate attendance
        self.total_meetings = Meeting.objects.filter(status='completed').count()
        self.total_meetings_attended = Attendance.objects.filter(
            member=self.member,
            status='present'
        ).count()
        
        if self.total_meetings > 0:
            self.attendance_rate = (self.total_meetings_attended / self.total_meetings) * 100
        
        self.save()
