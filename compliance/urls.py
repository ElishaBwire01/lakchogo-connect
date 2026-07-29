from django.urls import path
from . import views

app_name = 'compliance'

urlpatterns = [
    path('', views.index, name='index'),
    path('scorecard/', views.scorecard, name='scorecard'),
    path('member/<str:member_id>/', views.member_status, name='member_status'),
    path('member/<str:member_id>/check/', views.check_member, name='check_member'),
    path('member/<str:member_id>/json/', views.get_member_score_json, name='member_json'),
    path('rules/', views.rules, name='rules'),
    path('rules/create/', views.create_rule, name='create_rule'),
    path('alerts/', views.alerts, name='alerts'),
    path('alerts/<int:alert_id>/resolve/', views.resolve_alert, name='resolve_alert'),
    path('run-check/', views.run_compliance_check, name='run_check'),
    path('stats/json/', views.get_stats_json, name='stats_json'),
]
