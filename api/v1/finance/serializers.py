from rest_framework import serializers
from finance.models import Payment, PaymentCategory
from api.v1.members.serializers import MemberSerializer

class CategorySerializer(serializers.ModelSerializer):
    """Serializer for PaymentCategory model"""
    
    class Meta:
        model = PaymentCategory
        fields = [
            'id', 'name', 'description', 'default_amount',
            'frequency', 'is_mandatory_for_welfare',
            'is_active', 'color', 'icon', 'order',
            'created_at', 'updated_at'
        ]


class PaymentSerializer(serializers.ModelSerializer):
    """Serializer for Payment model"""
    member_details = MemberSerializer(source='member', read_only=True)
    category_details = CategorySerializer(source='category', read_only=True)
    recorded_by_name = serializers.SerializerMethodField()
    verified_by_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Payment
        fields = [
            'id', 'member', 'member_details', 'category', 'category_details',
            'amount', 'payment_method', 'transaction_ref', 'external_ref',
            'status', 'recorded_by', 'recorded_by_name',
            'verified_by', 'verified_by_name', 'verified_at',
            'receipt_url', 'receipt_file', 'notes',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_recorded_by_name(self, obj):
        return obj.recorded_by.get_full_name() if obj.recorded_by else None
    
    def get_verified_by_name(self, obj):
        return obj.verified_by.get_full_name() if obj.verified_by else None
    
    def create(self, validated_data):
        validated_data['recorded_by'] = self.context['request'].user
        validated_data['status'] = 'completed'
        return super().create(validated_data)
