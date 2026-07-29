from django.db import models
from django.conf import settings
from django.utils import timezone
from core.models import BaseModel
from members.models import Member

class BereavementEvent(BaseModel):
    """Bereavement/welfare events"""
    STATUS_CHOICES = (
        ('active', 'Active'),
        ('closed', 'Closed'),
        ('disbursed', 'Disbursed'),
        ('cancelled', 'Cancelled'),
    )
    
    event_code = models.CharField(max_length=20, unique=True, blank=True, help_text="Auto-generated event code")
    member = models.ForeignKey(
        Member,
        on_delete=models.CASCADE,
        related_name='bereavement_events',
        help_text="The member who is bereaved"
    )
    deceased_name = models.CharField(max_length=200, help_text="Full name of the deceased")
    relationship = models.CharField(max_length=100, help_text="Relationship to the member")
    date_of_death = models.DateField(help_text="Date of death")
    date_of_burial = models.DateField(null=True, blank=True, help_text="Date of burial")
    collection_target = models.DecimalField(max_digits=10, decimal_places=2, help_text="Target amount to collect")
    amount_collected = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    amount_disbursed = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    payout_date = models.DateField(null=True, blank=True)
    disbursement_notes = models.TextField(blank=True)
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_bereavements'
    )
    approved_at = models.DateTimeField(null=True, blank=True)
    description = models.TextField(blank=True, help_text="Additional details about the event")
    
    class Meta:
        db_table = 'bereavement_events'
        ordering = ['-created_at']
        verbose_name = 'Bereavement Event'
        verbose_name_plural = 'Bereavement Events'
    
    def __str__(self):
        return f"{self.event_code} - {self.deceased_name} ({self.member.get_full_name()})"
    
    def save(self, *args, **kwargs):
        if not self.event_code:
            # Generate event code: B-YYYY-XXXX
            year = timezone.now().year
            last_event = BereavementEvent.objects.filter(
                event_code__startswith=f'B-{year}'
            ).order_by('-event_code').first()
            
            if last_event:
                last_num = int(last_event.event_code.split('-')[2])
                new_num = last_num + 1
            else:
                new_num = 1
            
            self.event_code = f'B-{year}-{str(new_num).zfill(4)}'
        super().save(*args, **kwargs)
    
    @property
    def progress_percentage(self):
        if self.collection_target > 0:
            return (self.amount_collected / self.collection_target) * 100
        return 0
    
    @property
    def is_fully_collected(self):
        return self.amount_collected >= self.collection_target
    
    def approve(self, user):
        self.status = 'active'
        self.approved_by = user
        self.approved_at = timezone.now()
        self.save()
    
    def close(self):
        self.status = 'closed'
        self.save()
    
    def disburse(self, amount=None, notes=''):
        if amount:
            self.amount_disbursed = amount
        self.status = 'disbursed'
        self.payout_date = timezone.now().date()
        self.disbursement_notes = notes
        self.save()


class BereavementContribution(BaseModel):
    """Contributions to bereavement events"""
    CONTRIBUTION_TYPES = (
        ('member', 'Member Contribution'),
        ('public', 'Public Contribution'),
        ('group', 'Group Contribution'),
        ('other', 'Other'),
    )
    
    event = models.ForeignKey(
        BereavementEvent,
        on_delete=models.CASCADE,
        related_name='contributions'
    )
    contributor = models.ForeignKey(
        Member,
        on_delete=models.CASCADE,
        related_name='bereavement_contributions',
        null=True,
        blank=True,
        help_text="Member who contributed (if member)"
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    contribution_type = models.CharField(max_length=20, choices=CONTRIBUTION_TYPES, default='member')
    is_public_contribution = models.BooleanField(default=True)
    contributor_name = models.CharField(max_length=200, blank=True, help_text="Name for public contributions")
    contributor_phone = models.CharField(max_length=17, blank=True)
    payment_method = models.CharField(max_length=20, choices=(
        ('mpesa', 'M-Pesa'),
        ('airtel', 'Airtel Money'),
        ('cash', 'Cash'),
        ('bank', 'Bank Transfer'),
    ), default='cash')
    transaction_ref = models.CharField(max_length=50, blank=True)
    notes = models.TextField(blank=True)
    recorded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='recorded_contributions'
    )
    
    class Meta:
        db_table = 'bereavement_contributions'
        ordering = ['-created_at']
        verbose_name = 'Bereavement Contribution'
        verbose_name_plural = 'Bereavement Contributions'
    
    def __str__(self):
        if self.contributor:
            return f"{self.contributor.get_full_name()} - KES {self.amount} - {self.event.event_code}"
        return f"{self.contributor_name} - KES {self.amount} - {self.event.event_code}"
    
    def save(self, *args, **kwargs):
        if not self.contributor_name and self.contributor:
            self.contributor_name = self.contributor.get_full_name()
        super().save(*args, **kwargs)


class WelfareFund(BaseModel):
    """Welfare fund management"""
    FUND_TYPES = (
        ('general', 'General Welfare Fund'),
        ('emergency', 'Emergency Fund'),
        ('bereavement', 'Bereavement Fund'),
        ('development', 'Development Fund'),
    )
    
    name = models.CharField(max_length=100)
    fund_type = models.CharField(max_length=20, choices=FUND_TYPES)
    description = models.TextField(blank=True)
    balance = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    target_balance = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_funds'
    )
    
    class Meta:
        db_table = 'welfare_funds'
        ordering = ['name']
        verbose_name = 'Welfare Fund'
        verbose_name_plural = 'Welfare Funds'
    
    def __str__(self):
        return f"{self.name} - KES {self.balance}"
    
    def add_funds(self, amount, description='', user=None):
        """Add funds to the welfare fund"""
        self.balance += amount
        self.save()
        
        # Create transaction record
        from finance.models import Payment
        Payment.objects.create(
            member=None,
            category=None,
            amount=amount,
            payment_method='cash',
            status='completed',
            recorded_by=user,
            notes=f"Welfare Fund: {self.name} - {description}"
        )
        return self.balance
    
    def deduct_funds(self, amount, description='', user=None):
        """Deduct funds from the welfare fund"""
        if self.balance >= amount:
            self.balance -= amount
            self.save()
            return self.balance
        return None


class WelfareRequest(BaseModel):
    """Welfare requests from members"""
    REQUEST_TYPES = (
        ('bereavement', 'Bereavement Support'),
        ('medical', 'Medical Assistance'),
        ('education', 'Education Support'),
        ('emergency', 'Emergency Fund'),
        ('other', 'Other'),
    )
    
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('reviewing', 'Under Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('disbursed', 'Disbursed'),
    )
    
    member = models.ForeignKey(
        Member,
        on_delete=models.CASCADE,
        related_name='welfare_requests'
    )
    request_type = models.CharField(max_length=20, choices=REQUEST_TYPES)
    title = models.CharField(max_length=200)
    description = models.TextField()
    amount_requested = models.DecimalField(max_digits=10, decimal_places=2)
    amount_approved = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    supporting_documents = models.FileField(upload_to='welfare_docs/', null=True, blank=True)
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reviewed_requests'
    )
    reviewed_at = models.DateTimeField(null=True, blank=True)
    review_notes = models.TextField(blank=True)
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_requests'
    )
    approved_at = models.DateTimeField(null=True, blank=True)
    disbursed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='disbursed_requests'
    )
    disbursed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'welfare_requests'
        ordering = ['-created_at']
        verbose_name = 'Welfare Request'
        verbose_name_plural = 'Welfare Requests'
    
    def __str__(self):
        return f"{self.member.get_full_name()} - {self.title} - {self.status}"
    
    def approve(self, user, amount=None):
        self.status = 'approved'
        self.approved_by = user
        self.approved_at = timezone.now()
        if amount:
            self.amount_approved = amount
        self.save()
    
    def reject(self, user, notes=''):
        self.status = 'rejected'
        self.reviewed_by = user
        self.reviewed_at = timezone.now()
        self.review_notes = notes
        self.save()
    
    def disburse(self, user):
        self.status = 'disbursed'
        self.disbursed_by = user
        self.disbursed_at = timezone.now()
        self.save()
