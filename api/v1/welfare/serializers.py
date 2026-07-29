from rest_framework import serializers
from welfare.models import BereavementEvent, BereavementContribution
from api.v1.members.serializers import MemberSerializer

class BereavementContributionSerializer(serializers.ModelSerializer):
    """Serializer for BereavementContribution model"""
    contributor_details = MemberSerializer(source='contributor', read_only=True)
    recorded_by_name = serializers.SerializerMethodField()
    
    class Meta:
        model = BereavementContribution
        fields = [
            'id', 'event', 'contributor', 'contributor_details',
            'amount', 'contribution_type', 'is_public_contribution',
            'contributor_name', 'contributor_phone',
            'payment_method', 'transaction_ref', 'notes',
            'recorded_by', 'recorded_by_name', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_recorded_by_name(self, obj):
        return obj.recorded_by.get_full_name() if obj.recorded_by else None


class BereavementEventSerializer(serializers.ModelSerializer):
    """Serializer for BereavementEvent model"""
    member_details = MemberSerializer(source='member', read_only=True)
    contributions_count = serializers.SerializerMethodField()
    progress_percentage = serializers.SerializerMethodField()
    
    class Meta:
        model = BereavementEvent
        fields = [
            'id', 'event_code', 'member', 'member_details',
            'deceased_name', 'relationship', 'date_of_death',
            'date_of_burial', 'collection_target', 'amount_collected',
            'amount_disbursed', 'status', 'payout_date',
            'disbursement_notes', 'description',
            'contributions_count', 'progress_percentage',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'event_code', 'created_at', 'updated_at']
    
    def get_contributions_count(self, obj):
        return obj.contributions.count()
    
    def get_progress_percentage(self, obj):
        return obj.progress_percentage
