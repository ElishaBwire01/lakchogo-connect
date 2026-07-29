from django.urls import path
from . import views

app_name = 'members'

urlpatterns = [
    path('', views.list_members, name='list'),
    path('register/', views.register_member, name='register'),
    path('<str:member_id>/', views.member_detail, name='detail'),
    path('<str:member_id>/edit/', views.edit_member, name='edit'),
    path('search/', views.search_members, name='search'),
]
