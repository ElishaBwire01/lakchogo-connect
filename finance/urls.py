from django.urls import path
from . import views

app_name = 'finance'

urlpatterns = [
    path('', views.index, name='index'),
    path('categories/', views.category_list, name='category_list'),
    path('categories/create/', views.category_create, name='category_create'),
    path('categories/<int:category_id>/edit/', views.category_edit, name='category_edit'),
    path('record/', views.record_payment, name='record_payment'),
    path('payments/', views.payment_list, name='payment_list'),
    path('payments/history/', views.payment_history, name='payment_history'),
    path('payments/<int:payment_id>/', views.payment_detail, name='payment_detail'),
    path('payments/<int:payment_id>/approve/', views.payment_approve, name='payment_approve'),
    path('receipts/<int:payment_id>/', views.receipt_view, name='receipt_view'),
    path('receipts/<int:payment_id>/download/', views.receipt_download, name='receipt_download'),
    path('reminder/', views.send_reminder, name='send_reminder'),
    path('reminder/<str:member_id>/', views.send_reminder, name='send_reminder_member'),
    path('api/member/<str:member_id>/payments/', views.get_member_payments_json, name='member_payments_json'),
    path('api/category/stats/', views.get_category_stats_json, name='category_stats_json'),
]
