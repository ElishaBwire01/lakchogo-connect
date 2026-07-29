from django.urls import path
from . import views

app_name = 'welfare'

urlpatterns = [
    path('', views.index, name='index'),
    path('create/', views.create_event, name='create'),
    path('<int:event_id>/', views.detail, name='detail'),
    path('<int:event_id>/contribute/', views.add_contribution, name='add_contribution'),
    path('<int:event_id>/approve/', views.approve_event, name='approve_event'),
    path('<int:event_id>/stats/', views.get_event_stats, name='event_stats'),
    path('list/', views.list_events, name='list'),
    path('funds/', views.welfare_funds, name='funds'),
    path('requests/', views.welfare_requests, name='requests'),
    path('requests/create/', views.create_request, name='create_request'),
    path('requests/<int:request_id>/', views.request_detail, name='request_detail'),
    path('requests/<int:request_id>/approve/', views.approve_request, name='approve_request'),
]
