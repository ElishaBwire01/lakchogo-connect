from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    # Authentication
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    
    # Profile
    path('profile/', views.profile, name='profile'),
    path('profile/edit/', views.profile_edit, name='profile_edit'),
    
    # Password Reset - Complete Flow
    path('password-reset/', views.password_reset, name='password_reset'),
    path('password-reset/confirm-user/', views.password_reset_confirm_user, name='password_reset_confirm_user'),
    path('password-reset/verify/', views.password_reset_verify, name='password_reset_verify'),
    
    # Google Login
    path('google-login/', views.google_login, name='google_login'),
    
    # Admin - User Management
    path('manage/users/', views.manage_users, name='manage_users'),
    path('manage/users/<int:user_id>/toggle/', views.toggle_user_status, name='toggle_user_status'),
    path('manage/users/<int:user_id>/assign-role/', views.assign_role, name='assign_role'),
    
    # Admin - Role Management
    path('manage/roles/', views.manage_roles, name='manage_roles'),
    path('manage/roles/create/', views.create_role, name='create_role'),
    
    # API Endpoints
    path('api/user/<int:user_id>/roles/', views.get_user_roles, name='get_user_roles'),
    path('api/check-username/', views.check_username, name='check_username'),
]
