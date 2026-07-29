from django.db import models
from django.conf import settings
from core.models import BaseModel
from members.models import Member

class BereavementEvent(BaseModel):
    """Bereavement/welfare events"""
    STATUS_CHOICES = (
        ('active', 'Active'),
        ('closed', 'Closed'),
        ('disbursed', 'Disbursed'),
    )
    
    member = models.ForeignKey(
        Member,
        on_delete=models.CASCADE,
        related_name='bereavement_events',
        help_text="The member who is bereaved"
    )
    deceased_name = models.CharField(max_length=200)
    relationship = models.CharField(max_length=100)
    date_of_death = models.DateField()
    collection_target = models.DecimalField(max_digits=10, decimal_places=2)
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
    
    class Meta:
        db_table = 'bereavement_events'
        ordering = ['-created_at']
        verbose_name = 'Bereavement Event'
        verbose_name_plural = 'Bereavement Events'
    
    def __str__(self):
        return f"Bereavement: {self.deceased_name} - {self.member.get_full_name()}"
    
    @property
    def progress_percentage(self):
        if self.collection_target > 0:
            return (self.amount_collected / self.collection_target) * 100
        return 0


class BereavementContribution(BaseModel):
    """Contributions to bereavement events"""
    event = models.ForeignKey(
        BereavementEvent,
        on_delete=models.CASCADE,
        related_name='contributions'
    )
    contributor = models.ForeignKey(
        Member,
        on_delete=models.CASCADE,
        related_name='bereavement_contributions'
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    is_public_contribution = models.BooleanField(default=True)
    contributor_name = models.CharField(max_length=200, blank=True)
    contributor_phone = models.CharField(max_length=17, blank=True)
    
    class Meta:
        db_table = 'bereavement_contributions'
        ordering = ['-created_at']
        verbose_name = 'Bereavement Contribution'
        verbose_name_plural = 'Bereavement Contributions'
    
    def __str__(self):
        return f"{self.contributor.get_full_name()} - KES {self.amount}"
