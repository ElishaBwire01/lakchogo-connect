from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.db.models import Q

User = get_user_model()

class PhoneOrUsernameBackend(ModelBackend):
    """Custom authentication backend to allow login with phone or username"""
    
    def authenticate(self, request, username=None, password=None, **kwargs):
        if username is None:
            username = kwargs.get('phone')
        
        if username is None or password is None:
            return None
        
        try:
            # Try to find user by username or phone
            user = User.objects.get(
                Q(username=username) | Q(phone=username)
            )
        except User.DoesNotExist:
            # Run the default password hasher once to reduce timing differences
            User().set_password(password)
            return None
        
        if user.check_password(password) and self.user_can_authenticate(user):
            return user
        
        return None
    
    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
