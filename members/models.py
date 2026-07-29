from django.db import models
from django.conf import settings
from django.utils import timezone
from core.models import BaseModel
from core.constants import COMPLIANCE_STATUS_CHOICES

class Member(BaseModel):
    """Member model for LakChogo Welfare Group"""
    member_id = models.CharField(max_length=20, unique=True, blank=True)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='member'
    )
    next_of_kin_name = models.CharField(max_length=100, blank=True)
    next_of_kin_phone = models.CharField(max_length=17, blank=True)
    next_of_kin_relationship = models.CharField(max_length=50, blank=True)
    date_joined = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=20, default='active', choices=(
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('suspended', 'Suspended'),
    ))
    compliance_status = models.CharField(
        max_length=20, 
        choices=COMPLIANCE_STATUS_CHOICES, 
        default='green'
    )
    notes = models.TextField(blank=True)
    
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
            if last_member:
                last_id = int(last_member.member_id.split('-')[1])
                new_id = last_id + 1
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
