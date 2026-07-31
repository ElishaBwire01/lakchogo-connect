from django.urls import path
from . import views

app_name = 'meetings'

urlpatterns = [
    path('', views.index, name='index'),
    path('schedule/', views.schedule, name='schedule'),
    path('<int:meeting_id>/', views.detail, name='detail'),
    path('<int:meeting_id>/attendance/', views.take_attendance, name='attendance'),
    path('<int:meeting_id>/minutes/', views.upload_minutes, name='upload_minutes'),
    path('<int:meeting_id>/edit/', views.edit_meeting, name='edit'),
    path('<int:meeting_id>/delete/', views.delete_meeting, name='delete'),
    # QR Code endpoints
    path('<int:meeting_id>/qr/', views.qr_code_display, name='qr_display'),
    path('<int:meeting_id>/qr-image/', views.generate_qr_image, name='qr_image'),
    path('<int:meeting_id>/qr-checkin/', views.qr_check_in, name='qr_check_in'),
    path('<int:meeting_id>/summary/', views.get_attendance_summary, name='summary'),
]
