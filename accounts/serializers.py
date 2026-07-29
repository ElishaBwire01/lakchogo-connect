from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Role, UserRole

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
            'is_active', 'is_committee', 'date_joined', 'roles'
        ]
    
    def get_full_name(self, obj):
        return obj.get_full_name()
    
    def get_roles(self, obj):
        user_roles = UserRole.objects.filter(
            user=obj,
            is_active=True
        ).select_related('role')
        return [{'id': ur.role.id, 'name': ur.role.name} for ur in user_roles]

class UserCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating users"""
    password = serializers.CharField(write_only=True)
    password_confirm = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = [
            'username', 'first_name', 'last_name', 'phone',
            'email', 'id_number', 'password', 'password_confirm'
        ]
    
    def validate(self, data):
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError("Passwords do not match")
        return data
    
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        user = User.objects.create_user(**validated_data)
        user.set_password(password)
        user.save()
        return user

class RoleSerializer(serializers.ModelSerializer):
    """Serializer for Role model"""
    class Meta:
        model = Role
        fields = ['id', 'name', 'description', 'is_default', 'created_at']

class UserRoleSerializer(serializers.ModelSerializer):
    """Serializer for UserRole model"""
    user = UserSerializer(read_only=True)
    role = RoleSerializer(read_only=True)
    
    class Meta:
        model = UserRole
        fields = ['id', 'user', 'role', 'assigned_by', 'assigned_at', 'is_active']
