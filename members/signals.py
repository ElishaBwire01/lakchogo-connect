from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from .models import Member, MemberContributionSummary
from django.contrib.auth import get_user_model

User = get_user_model()

@receiver(post_save, sender=User)
def create_member_from_user(sender, instance, created, **kwargs):
    """Create member when a user is created (if applicable)"""
    if created and not hasattr(instance, 'member'):
        # Check if user should be a member
        pass

@receiver(post_save, sender=Member)
def create_contribution_summary(sender, instance, created, **kwargs):
    """Create contribution summary when a member is created"""
    if created:
        MemberContributionSummary.objects.create(member=instance)
        
        # Create compliance score
        from compliance.models import ComplianceScore
        ComplianceScore.objects.create(
            member=instance,
            status='green',
            score=100.00
        )

@receiver(post_save, sender=Member)
def update_related_data(sender, instance, **kwargs):
    """Update related data when member is updated"""
    # Update compliance status if needed
    if instance.status == 'inactive' and instance.compliance_status != 'red':
        instance.compliance_status = 'red'
        instance.save(update_fields=['compliance_status'])
    elif instance.status == 'active' and instance.compliance_status == 'red':
        # This should be updated by compliance service
        pass
