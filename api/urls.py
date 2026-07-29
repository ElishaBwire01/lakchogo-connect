from django.urls import path, include
from rest_framework.authtoken import views as auth_views
from rest_framework.documentation import include_docs_urls

app_name = 'api'

urlpatterns = [
    # API version 1
    path('v1/', include('api.v1.urls')),
    
    # Authentication
    path('auth/', include('rest_framework.urls')),
    path('auth/token/', auth_views.obtain_auth_token, name='api_token_auth'),
    
    # API Documentation (optional)
    # path('docs/', include_docs_urls(title='LakChogo API')),
]
