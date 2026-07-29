from django.urls import path
from . import views

app_name = 'members'

urlpatterns = [
    path('', views.list_members, name='list'),
    path('register/', views.register_member, name='register'),
    path('search/', views.search_members, name='search'),
    path('<str:member_id>/', views.member_detail, name='detail'),
    path('<str:member_id>/edit/', views.edit_member, name='edit'),
    path('<str:member_id>/note/', views.add_note, name='add_note'),
    path('<str:member_id>/status/', views.member_status, name='status'),
    path('<str:member_id>/update-status/', views.update_status, name='update_status'),
    path('api/<str:member_id>/', views.get_member_json, name='api_member'),
    path('api/all/', views.get_members_json, name='api_all'),
]
