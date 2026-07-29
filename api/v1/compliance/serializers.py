from rest_framework import serializers
from compliance.models import ComplianceScore, ComplianceAlert, ComplianceRule
from api.v1.members.serializers import MemberSerializer

class ComplianceRuleSerializer(serializers.ModelSerializer):
    """Serializer for ComplianceRule model"""
    
    class Meta:
        model = ComplianceRule
        fields = [
            'id', 'name', 'description', 'rule_type',
            'min_attendance_percentage', 'grace_period_days',
            'penalty_points', 'is_active', 'order',
            'created_at', 'updated_at'
        ]


class ComplianceScoreSerializer(serializers.ModelSerializer):
    """Serializer for ComplianceScore model"""
    member_details = MemberSerializer(source='member', read_only=True)
    status_display = serializers.SerializerMethodField()
    
    class Meta:
        model = ComplianceScore
        fields = [
            'id', 'member', 'member_details', 'status', 'status_display',
            'score', 'payment_compliance', 'attendance_compliance',
            'warnings', 'last_checked', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'last_checked', 'created_at', 'updated_at']
    
    def get_status_display(self, obj):
        return obj.get_status_display()


class ComplianceAlertSerializer(serializers.ModelSerializer):
    """Serializer for ComplianceAlert model"""
    member_details = MemberSerializer(source='member', read_only=True)
    
    class Meta:
        model = ComplianceAlert
        fields = [
            'id', 'member', 'member_details', 'alert_type',
            'priority', 'message', 'is_resolved', 'resolved_at',
            'resolution_notes', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
