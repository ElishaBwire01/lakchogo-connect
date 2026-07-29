from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from .services import DashboardService

@login_required
def index(request):
    """Main dashboard view"""
    dashboard_data = DashboardService.get_user_dashboard_data(request.user)
    
    context = {
        'user': request.user,
        'title': 'Dashboard',
        'dashboard': dashboard_data,
        'is_admin': request.user.is_superuser or request.user.is_staff,
    }
    return render(request, 'dashboard/index.html', context)


@login_required
@staff_member_required
def admin_dashboard(request):
    """Admin dashboard view"""
    dashboard_data = DashboardService.get_user_dashboard_data(request.user)
    
    context = {
        'user': request.user,
        'title': 'Admin Dashboard',
        'dashboard': dashboard_data,
        'is_admin': True,
    }
    return render(request, 'dashboard/admin_dashboard.html', context)


@login_required
def member_dashboard(request):
    """Member-specific dashboard"""
    dashboard_data = DashboardService.get_user_dashboard_data(request.user)
    
    # Add member-specific data
    try:
        member = request.user.member
        dashboard_data['member_profile'] = {
            'member_id': member.member_id,
            'status': member.status,
            'compliance': member.compliance_status,
        }
    except:
        dashboard_data['member_profile'] = None
    
    context = {
        'user': request.user,
        'title': 'Member Dashboard',
        'dashboard': dashboard_data,
    }
    return render(request, 'dashboard/member_dashboard.html', context)


@login_required
def treasurer_dashboard(request):
    """Treasurer dashboard"""
    dashboard_data = DashboardService.get_user_dashboard_data(request.user)
    
    # Add treasurer-specific data
    from finance.models import PaymentCategory
    
    dashboard_data['payment_categories'] = PaymentCategory.objects.filter(is_active=True)
    dashboard_data['pending_payments'] = Payment.objects.filter(
        status='pending'
    ).count()
    
    context = {
        'user': request.user,
        'title': 'Treasurer Dashboard',
        'dashboard': dashboard_data,
    }
    return render(request, 'dashboard/treasurer_dashboard.html', context)


@login_required
def secretary_dashboard(request):
    """Secretary dashboard"""
    dashboard_data = DashboardService.get_user_dashboard_data(request.user)
    
    # Add secretary-specific data
    from meetings.models import Meeting
    
    dashboard_data['upcoming_meetings'] = Meeting.objects.filter(
        date__gte=timezone.now(),
        status='scheduled'
    )[:5]
    
    context = {
        'user': request.user,
        'title': 'Secretary Dashboard',
        'dashboard': dashboard_data,
    }
    return render(request, 'dashboard/secretary_dashboard.html', context)


@login_required
def welfare_dashboard(request):
    """Welfare officer dashboard"""
    dashboard_data = DashboardService.get_user_dashboard_data(request.user)
    
    # Add welfare-specific data
    from welfare.models import BereavementEvent
    
    dashboard_data['active_events'] = BereavementEvent.objects.filter(
        status='active'
    )
    
    context = {
        'user': request.user,
        'title': 'Welfare Dashboard',
        'dashboard': dashboard_data,
    }
    return render(request, 'dashboard/welfare_dashboard.html', context)


def handler404(request, exception):
    """Custom 404 error handler"""
    return render(request, '404.html', {'title': 'Page Not Found'}, status=404)


def handler500(request):
    """Custom 500 error handler"""
    return render(request, '500.html', {'title': 'Server Error'}, status=500)
