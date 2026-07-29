from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .auth.views import UserViewSet, RoleViewSet
from .members.views import MemberViewSet
from .finance.views import PaymentViewSet, CategoryViewSet
from .meetings.views import MeetingViewSet
from .compliance.views import ComplianceViewSet
from .welfare.views import WelfareViewSet
from .reports.views import ReportViewSet

# Create router
router = DefaultRouter()
router.register(r'auth/users', UserViewSet)
router.register(r'auth/roles', RoleViewSet)
router.register(r'members', MemberViewSet)
router.register(r'payments', PaymentViewSet)
router.register(r'categories', CategoryViewSet)
router.register(r'meetings', MeetingViewSet)
router.register(r'compliance', ComplianceViewSet)
router.register(r'welfare', WelfareViewSet)
# Reports viewset doesn't have a queryset, register with basename
router.register(r'reports', ReportViewSet, basename='reports')

urlpatterns = [
    path('', include(router.urls)),
]
