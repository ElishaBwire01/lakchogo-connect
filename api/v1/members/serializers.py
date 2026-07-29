from rest_framework import serializers
from members.models import Member, MemberNote
from api.v1.auth.serializers import UserSerializer

class MemberSerializer(serializers.ModelSerializer):
    """Serializer for Member model"""
    full_name = serializers.SerializerMethodField()
    user = UserSerializer(read_only=True)
    compliance_status_display = serializers.SerializerMethodField()
    
    class Meta:
        model = Member
        fields = [
            'id', 'member_id', 'user', 'full_name',
            'status', 'compliance_status', 'compliance_status_display',
            'date_joined', 'next_of_kin_name', 'next_of_kin_phone',
            'next_of_kin_relationship', 'date_of_birth', 'gender',
            'occupation', 'address', 'notes',
            'emergency_contact_name', 'emergency_contact_phone',
            'emergency_contact_relationship', 'created_at', 'updated_at'
        ]
    
    def get_full_name(self, obj):
        return obj.get_full_name()
    
    def get_compliance_status_display(self, obj):
        return obj.get_compliance_status_display()


class MemberCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating members"""
    username = serializers.CharField(write_only=True)
    first_name = serializers.CharField(write_only=True)
    last_name = serializers.CharField(write_only=True)
    phone = serializers.CharField(write_only=True)
    id_number = serializers.CharField(write_only=True)
    email = serializers.EmailField(write_only=True, required=False)
    password = serializers.CharField(write_only=True)
    
    class Meta:
        model = Member
        fields = [
            'username', 'first_name', 'last_name', 'phone',
            'id_number', 'email', 'password',
            'next_of_kin_name', 'next_of_kin_phone',
            'next_of_kin_relationship', 'date_of_birth',
            'gender', 'occupation', 'address',
            'emergency_contact_name', 'emergency_contact_phone',
            'emergency_contact_relationship'
        ]
    
    def validate_username(self, value):
        from django.contrib.auth import get_user_model
        User = get_user_model()
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError('Username already exists')
        return value
    
    def validate_phone(self, value):
        from django.contrib.auth import get_user_model
        User = get_user_model()
        if User.objects.filter(phone=value).exists():
            raise serializers.ValidationError('Phone number already registered')
        return value
    
    def validate_id_number(self, value):
        from django.contrib.auth import get_user_model
        User = get_user_model()
        if User.objects.filter(id_number=value).exists():
            raise serializers.ValidationError('ID number already registered')
        return value
    
    def create(self, validated_data):
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        password = validated_data.pop('password')
        username = validated_data.pop('username')
        first_name = validated_data.pop('first_name')
        last_name = validated_data.pop('last_name')
        phone = validated_data.pop('phone')
        id_number = validated_data.pop('id_number')
        email = validated_data.pop('email', '')
        
        user = User.objects.create_user(
            username=username,
            first_name=first_name,
            last_name=last_name,
            phone=phone,
            id_number=id_number,
            email=email,
            password=password
        )
        
        member = Member.objects.create(
            user=user,
            **validated_data
        )
        
        return member


class MemberNoteSerializer(serializers.ModelSerializer):
    """Serializer for MemberNote model"""
    author_name = serializers.SerializerMethodField()
    
    class Meta:
        model = MemberNote
        fields = [
            'id', 'member', 'author', 'author_name',
            'content', 'is_private', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_author_name(self, obj):
        return obj.author.get_full_name() if obj.author else 'Unknown'
