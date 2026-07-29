from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
    path('', views.index, name='index'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('members/', views.member_report, name='members'),
    path('payments/', views.payment_report, name='payments'),
    path('attendance/', views.attendance_report, name='attendance'),
    path('compliance/', views.compliance_report, name='compliance'),
    path('welfare/', views.welfare_report, name='welfare'),
    path('generate/', views.generate_report, name='generate'),
    path('<int:report_id>/', views.report_detail, name='detail'),
    path('<int:report_id>/download/', views.download_report, name='download'),
    path('<int:report_id>/delete/', views.delete_report, name='delete'),
]
