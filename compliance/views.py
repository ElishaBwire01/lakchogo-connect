from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Count, Q, Sum
from django.core.paginator import Paginator
from django.utils import timezone
from .models import ComplianceRule, ComplianceScore, ComplianceAlert, ComplianceReport
from members.models import Member
from .services import ComplianceService

@login_required
def index(request):
    """Compliance dashboard"""
    total_members = Member.objects.filter(status='active').count()
    
    # Get compliance statistics
    green = ComplianceScore.objects.filter(status='green').count()
    yellow = ComplianceScore.objects.filter(status='yellow').count()
    red = ComplianceScore.objects.filter(status='red').count()
    
    # Get recent alerts
    recent_alerts = ComplianceAlert.objects.filter(
        is_resolved=False
    ).order_by('-created_at')[:10]
    
    # Get compliance rate
    compliance_rate = (green / total_members * 100) if total_members > 0 else 0
    
    context = {
        'title': 'Compliance Dashboard',
        'total_members': total_members,
        'green': green,
        'yellow': yellow,
        'red': red,
        'compliance_rate': compliance_rate,
        'recent_alerts': recent_alerts,
        'has_alerts': recent_alerts.exists(),
    }
    return render(request, 'compliance/index.html', context)


@login_required
def scorecard(request):
    """View member compliance scorecard"""
    members = Member.objects.filter(status='active')
    
    # Get search query
    query = request.GET.get('q')
    if query:
        members = members.filter(
            Q(user__first_name__icontains=query) |
            Q(user__last_name__icontains=query) |
            Q(member_id__icontains=query)
        )
    
    # Annotate with compliance data
    member_data = []
    for member in members:
        try:
            score = ComplianceScore.objects.get(member=member)
            member_data.append({
                'member': member,
                'score': score,
                'status': score.status,
                'payment_score': score.payment_compliance,
                'attendance_score': score.attendance_compliance,
                'warnings': score.warnings,
            })
        except ComplianceScore.DoesNotExist:
            member_data.append({
                'member': member,
                'score': None,
                'status': 'unknown',
                'payment_score': 0,
                'attendance_score': 0,
                'warnings': [],
            })
    
    # Filter by status
    status_filter = request.GET.get('status')
    if status_filter and status_filter != 'all':
        member_data = [m for m in member_data if m['status'] == status_filter]
    
    context = {
        'title': 'Compliance Scorecard',
        'members': member_data,
        'query': query,
        'status_filter': status_filter,
    }
    return render(request, 'compliance/scorecard.html', context)


@login_required
def member_status(request, member_id):
    """View individual member compliance status"""
    member = get_object_or_404(Member, member_id=member_id)
    score = get_object_or_404(ComplianceScore, member=member)
    
    # Get alerts for this member
    alerts = ComplianceAlert.objects.filter(
        member=member,
        is_resolved=False
    ).order_by('-created_at')
    
    # Get compliance history (last 30 days)
    history = ComplianceService.get_member_history(member)
    
    context = {
        'title': f'Compliance Status - {member.get_full_name()}',
        'member': member,
        'score': score,
        'alerts': alerts,
        'history': history,
    }
    return render(request, 'compliance/member_status.html', context)


@login_required
def rules(request):
    """Manage compliance rules"""
    rules = ComplianceRule.objects.filter(is_active=True).order_by('order')
    
    context = {
        'title': 'Compliance Rules',
        'rules': rules,
    }
    return render(request, 'compliance/rules.html', context)


@login_required
def create_rule(request):
    """Create a new compliance rule"""
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        rule_type = request.POST.get('rule_type')
        target_category_id = request.POST.get('target_category')
        min_attendance = request.POST.get('min_attendance')
        grace_period = request.POST.get('grace_period')
        penalty_points = request.POST.get('penalty_points')
        order = request.POST.get('order')
        
        rule = ComplianceRule.objects.create(
            name=name,
            description=description,
            rule_type=rule_type,
            target_category_id=target_category_id or None,
            min_attendance_percentage=min_attendance or 75,
            grace_period_days=grace_period or 30,
            penalty_points=penalty_points or 10,
            order=order or 0,
            is_active=True
        )
        
        messages.success(request, f'Rule "{name}" created successfully!')
        return redirect('compliance:rules')
    
    from finance.models import PaymentCategory
    categories = PaymentCategory.objects.filter(is_active=True)
    
    context = {
        'title': 'Create Compliance Rule',
        'categories': categories,
    }
    return render(request, 'compliance/create_rule.html', context)


@login_required
def alerts(request):
    """View all compliance alerts"""
    alerts = ComplianceAlert.objects.all().order_by('-created_at')
    
    # Filter by resolved status
    resolved = request.GET.get('resolved')
    if resolved == 'true':
        alerts = alerts.filter(is_resolved=True)
    elif resolved == 'false':
        alerts = alerts.filter(is_resolved=False)
    
    # Filter by member
    member_id = request.GET.get('member')
    if member_id:
        alerts = alerts.filter(member__member_id=member_id)
    
    paginator = Paginator(alerts, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'title': 'Compliance Alerts',
        'alerts': page_obj,
        'resolved': resolved,
    }
    return render(request, 'compliance/alerts.html', context)


@login_required
def resolve_alert(request, alert_id):
    """Resolve a compliance alert"""
    alert = get_object_or_404(ComplianceAlert, id=alert_id)
    
    if request.method == 'POST':
        notes = request.POST.get('notes', '')
        alert.resolve(request.user, notes)
        messages.success(request, 'Alert resolved successfully!')
        return redirect('compliance:alerts')
    
    context = {
        'title': 'Resolve Alert',
        'alert': alert,
    }
    return render(request, 'compliance/resolve_alert.html', context)


@login_required
def run_compliance_check(request):
    """Run compliance check for all members"""
    if request.method == 'POST':
        try:
            result = ComplianceService.check_all_members()
            messages.success(request, f'Compliance check completed! {result["updated"]} members updated.')
        except Exception as e:
            messages.error(request, f'Error running compliance check: {str(e)}')
        
        return redirect('compliance:index')
    
    context = {
        'title': 'Run Compliance Check',
    }
    return render(request, 'compliance/run_check.html', context)


@login_required
def get_stats_json(request):
    """Get compliance statistics as JSON"""
    total = Member.objects.filter(status='active').count()
    green = ComplianceScore.objects.filter(status='green').count()
    yellow = ComplianceScore.objects.filter(status='yellow').count()
    red = ComplianceScore.objects.filter(status='red').count()
    
    data = {
        'total': total,
        'green': green,
        'yellow': yellow,
        'red': red,
        'compliance_rate': (green / total * 100) if total > 0 else 0,
        'alerts': ComplianceAlert.objects.filter(is_resolved=False).count(),
    }
    return JsonResponse(data)


@login_required
def get_member_score_json(request, member_id):
    """Get member compliance score as JSON"""
    member = get_object_or_404(Member, member_id=member_id)
    try:
        score = ComplianceScore.objects.get(member=member)
        data = {
            'member_id': member.member_id,
            'name': member.get_full_name(),
            'status': score.status,
            'score': float(score.score),
            'payment_score': float(score.payment_compliance),
            'attendance_score': float(score.attendance_compliance),
            'warnings': score.warnings,
        }
    except ComplianceScore.DoesNotExist:
        data = {
            'member_id': member.member_id,
            'name': member.get_full_name(),
            'status': 'unknown',
            'score': 0,
            'payment_score': 0,
            'attendance_score': 0,
            'warnings': [],
        }
    return JsonResponse(data)


@login_required
def check_member(request, member_id):
    """Manually check compliance for a single member"""
    member = get_object_or_404(Member, member_id=member_id)
    
    if request.method == 'POST':
        try:
            result = ComplianceService.check_member(member)
            messages.success(request, f'Compliance check completed for {member.get_full_name()}')
        except Exception as e:
            messages.error(request, f'Error: {str(e)}')
        
        return redirect('compliance:member_status', member_id=member.member_id)
    
    context = {
        'title': f'Check Compliance - {member.get_full_name()}',
        'member': member,
    }
    return render(request, 'compliance/check_member.html', context)
