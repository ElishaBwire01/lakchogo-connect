from django.urls import path
from . import views

app_name = 'welfare'

urlpatterns = [
    path('', views.index, name='index'),
    path('create/', views.create_event, name='create'),
    path('<int:event_id>/', views.event_detail, name='detail'),
]
