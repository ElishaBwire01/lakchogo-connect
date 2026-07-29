from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.hashers import make_password
from django.db.models import Q
from .serializers import UserSerializer, UserCreateSerializer, RoleSerializer
from accounts.models import Role, UserRole

User = get_user_model()

class UserViewSet(viewsets.ModelViewSet):
    """API endpoint for users"""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Filter users"""
        queryset = User.objects.all()
        
        # Search
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(username__icontains=search) |
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search) |
                Q(phone__icontains=search)
            )
        
        return queryset
    
    def get_serializer_class(self):
        """Use different serializer for create"""
        if self.action == 'create':
            return UserCreateSerializer
        return UserSerializer
    
    @action(detail=False, methods=['post'], permission_classes=[permissions.AllowAny])
    def register(self, request):
        """Register a new user"""
        serializer = UserCreateSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            token, created = Token.objects.get_or_create(user=user)
            return Response({
                'status': 'success',
                'user': UserSerializer(user).data,
                'token': token.key
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'], permission_classes=[permissions.AllowAny])
    def login(self, request):
        """Login user"""
        username = request.data.get('username')
        password = request.data.get('password')
        
        if not username or not password:
            return Response({
                'status': 'error',
                'message': 'Username and password required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        user = authenticate(request, username=username, password=password)
        
        if user:
            token, created = Token.objects.get_or_create(user=user)
            return Response({
                'status': 'success',
                'user': UserSerializer(user).data,
                'token': token.key
            })
        
        return Response({
            'status': 'error',
            'message': 'Invalid credentials'
        }, status=status.HTTP_401_UNAUTHORIZED)
    
    @action(detail=False, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def logout(self, request):
        """Logout user"""
        try:
            Token.objects.filter(user=request.user).delete()
        except:
            pass
        return Response({'status': 'success', 'message': 'Logged out'})
    
    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def me(self, request):
        """Get current user"""
        serializer = UserSerializer(request.user)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def change_password(self, request, pk=None):
        """Change user password"""
        user = self.get_object()
        old_password = request.data.get('old_password')
        new_password = request.data.get('new_password')
        
        if not user.check_password(old_password):
            return Response({
                'status': 'error',
                'message': 'Old password is incorrect'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        user.set_password(new_password)
        user.save()
        
        return Response({'status': 'success', 'message': 'Password changed'})


class RoleViewSet(viewsets.ModelViewSet):
    """API endpoint for roles"""
    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def assign_user(self, request, pk=None):
        """Assign role to user"""
        role = self.get_object()
        user_id = request.data.get('user_id')
        
        if not user_id:
            return Response({
                'status': 'error',
                'message': 'User ID required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({
                'status': 'error',
                'message': 'User not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Deactivate existing roles
        UserRole.objects.filter(user=user, is_active=True).update(is_active=False)
        
        # Assign new role
        UserRole.objects.create(
            user=user,
            role=role,
            assigned_by=request.user
        )
        
        return Response({'status': 'success', 'message': f'Role {role.name} assigned to {user.username}'})
    
    @action(detail=True, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def users(self, request, pk=None):
        """Get users with this role"""
        role = self.get_object()
        user_roles = UserRole.objects.filter(role=role, is_active=True)
        users = [ur.user for ur in user_roles]
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)
