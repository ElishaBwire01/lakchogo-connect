"""
LakChogo Connect URL Configuration
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', RedirectView.as_view(url='dashboard/', permanent=False)),
    path('dashboard/', include('dashboard.urls')),
    path('accounts/', include('accounts.urls')),
    path('members/', include('members.urls')),
    path('finance/', include('finance.urls')),
    path('meetings/', include('meetings.urls')),
    path('compliance/', include('compliance.urls')),
    path('welfare/', include('welfare.urls')),
    path('reports/', include('reports.urls')),
    path('communications/', include('communications.urls')),
    path('api/', include('api.urls')),
    # Google OAuth URLs
    path('accounts/', include('allauth.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Error handlers
handler400 = 'dashboard.views.handler400'
handler403 = 'dashboard.views.handler403'
handler404 = 'dashboard.views.handler404'
handler500 = 'dashboard.views.handler500'
