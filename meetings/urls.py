from django.urls import path
from . import views

app_name = 'meetings'

urlpatterns = [
    path('', views.index, name='index'),
    path('schedule/', views.schedule, name='schedule'),
    path('<int:meeting_id>/', views.meeting_detail, name='detail'),
    path('<int:meeting_id>/attendance/', views.take_attendance, name='attendance'),
]
