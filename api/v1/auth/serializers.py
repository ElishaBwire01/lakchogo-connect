from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from accounts.models import Role, UserRole

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model"""
    full_name = serializers.SerializerMethodField()
    roles = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'first_name', 'last_name', 'full_name',
            'phone', 'email', 'id_number', 'profile_picture',
            'is_active', 'is_committee', 'is_staff', 'is_superuser',
            'date_joined', 'last_login', 'roles'
        ]
        read_only_fields = ['date_joined', 'last_login']
    
    def get_full_name(self, obj):
        return obj.get_full_name()
    
    def get_roles(self, obj):
        user_roles = UserRole.objects.filter(
            user=obj,
            is_active=True
        ).select_related('role')
        return [{
            'id': ur.role.id,
            'name': ur.role.name
        } for ur in user_roles]


class UserCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating users"""
    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password]
    )
    password_confirm = serializers.CharField(
        write_only=True,
        required=True
    )
    
    class Meta:
        model = User
        fields = [
            'username', 'first_name', 'last_name', 'phone',
            'email', 'id_number', 'password', 'password_confirm'
        ]
    
    def validate(self, data):
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError({
                'password_confirm': 'Passwords do not match'
            })
        return data
    
    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError('Username already exists')
        return value
    
    def validate_phone(self, value):
        if User.objects.filter(phone=value).exists():
            raise serializers.ValidationError('Phone number already registered')
        return value
    
    def validate_id_number(self, value):
        if User.objects.filter(id_number=value).exists():
            raise serializers.ValidationError('ID number already registered')
        return value
    
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        user = User.objects.create_user(**validated_data)
        user.set_password(password)
        user.save()
        return user


class RoleSerializer(serializers.ModelSerializer):
    """Serializer for Role model"""
    user_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Role
        fields = [
            'id', 'name', 'description', 'is_default',
            'created_at', 'updated_at', 'user_count'
        ]
    
    def get_user_count(self, obj):
        return UserRole.objects.filter(role=obj, is_active=True).count()
