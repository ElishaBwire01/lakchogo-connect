from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import JsonResponse, HttpResponse
from django.db.models import Sum, Count, Q
from django.utils import timezone
from datetime import datetime, timedelta
from .models import PaymentCategory, Payment, PaymentReceipt, PaymentReminder
from members.models import Member
from accounts.decorators import admin_required, permission_required

@login_required
def index(request):
    """Finance dashboard"""
    total_payments = Payment.objects.filter(status='completed').aggregate(
        total=Sum('amount')
    )['total'] or 0
    
    pending_payments = Payment.objects.filter(status='pending').count()
    
    monthly_payments = Payment.objects.filter(
        status='completed',
        created_at__gte=timezone.now() - timedelta(days=30)
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    categories = PaymentCategory.objects.filter(is_active=True)
    
    context = {
        'title': 'Finance Dashboard',
        'total_payments': total_payments,
        'pending_payments': pending_payments,
        'monthly_payments': monthly_payments,
        'categories': categories,
        'total_categories': categories.count(),
    }
    return render(request, 'finance/index.html', context)


@login_required
def category_list(request):
    """List all payment categories"""
    categories = PaymentCategory.objects.filter(is_active=True).order_by('order')
    
    context = {
        'title': 'Payment Categories',
        'categories': categories,
    }
    return render(request, 'finance/categories/list.html', context)


@login_required
@permission_required('can_manage_categories')
def category_create(request):
    """Create a new payment category - Admin only"""
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        default_amount = request.POST.get('default_amount')
        frequency = request.POST.get('frequency')
        is_mandatory = request.POST.get('is_mandatory') == 'on'
        color = request.POST.get('color')
        icon = request.POST.get('icon')
        
        category = PaymentCategory.objects.create(
            name=name,
            description=description,
            default_amount=default_amount or 0,
            frequency=frequency or 'one-time',
            is_mandatory_for_welfare=is_mandatory,
            color=color or 'primary',
            icon=icon or 'fa-money-bill',
            is_active=True
        )
        
        messages.success(request, f'Category "{name}" created successfully!')
        return redirect('finance:category_list')
    
    context = {
        'title': 'Create Payment Category',
    }
    return render(request, 'finance/categories/create.html', context)


@login_required
@permission_required('can_manage_categories')
def category_edit(request, category_id):
    """Edit a payment category - Admin only"""
    category = get_object_or_404(PaymentCategory, id=category_id)
    
    if request.method == 'POST':
        category.name = request.POST.get('name')
        category.description = request.POST.get('description')
        category.default_amount = request.POST.get('default_amount') or 0
        category.frequency = request.POST.get('frequency') or 'one-time'
        category.is_mandatory_for_welfare = request.POST.get('is_mandatory') == 'on'
        category.color = request.POST.get('color') or 'primary'
        category.icon = request.POST.get('icon') or 'fa-money-bill'
        category.is_active = request.POST.get('is_active') == 'on'
        category.save()
        
        messages.success(request, f'Category "{category.name}" updated successfully!')
        return redirect('finance:category_list')
    
    context = {
        'title': f'Edit Category: {category.name}',
        'category': category,
    }
    return render(request, 'finance/categories/edit.html', context)


@login_required
def record_payment(request):
    """Record a new payment - Auto-populates current user"""
    try:
        member = Member.objects.get(user=request.user)
    except Member.DoesNotExist:
        messages.error(request, 'You are not registered as a member. Please contact admin.')
        return redirect('dashboard:index')
    
    categories = PaymentCategory.objects.filter(is_active=True)
    
    if request.method == 'POST':
        category_id = request.POST.get('category_id')
        amount = request.POST.get('amount')
        payment_method = request.POST.get('payment_method')
        transaction_ref = request.POST.get('transaction_ref')
        notes = request.POST.get('notes')
        
        if not all([category_id, amount]):
            messages.error(request, 'Please fill in all required fields.')
            return render(request, 'finance/record_payment.html', {
                'member': member,
                'categories': categories,
                'title': 'Record Payment',
            })
        
        category = get_object_or_404(PaymentCategory, id=category_id)
        
        is_admin = request.user.is_admin or request.user.is_superuser
        is_treasurer = request.user.is_treasurer
        
        if is_admin or is_treasurer:
            status = 'completed'
            verified_by = request.user
            verified_at = timezone.now()
        else:
            status = 'pending'
            verified_by = None
            verified_at = None
        
        payment = Payment.objects.create(
            member=member,
            category=category,
            amount=amount,
            payment_method=payment_method or 'cash',
            transaction_ref=transaction_ref or '',
            status=status,
            recorded_by=request.user,
            verified_by=verified_by,
            verified_at=verified_at,
            notes=notes or ''
        )
        
        if status == 'completed':
            messages.success(request, f'Payment of KES {amount} recorded successfully!')
        else:
            messages.info(request, f'Payment of KES {amount} recorded and pending admin approval.')
        
        return redirect('finance:payment_detail', payment_id=payment.id)
    
    context = {
        'title': 'Record Payment',
        'member': member,
        'categories': categories,
    }
    return render(request, 'finance/record_payment.html', context)


@login_required
def payment_list(request):
    """List all payments - Users see their own, Admins see all"""
    payments = Payment.objects.all().order_by('-created_at')
    
    if not request.user.is_admin and not request.user.is_superuser:
        try:
            member = Member.objects.get(user=request.user)
            payments = payments.filter(member=member)
        except Member.DoesNotExist:
            payments = Payment.objects.none()
    
    status_filter = request.GET.get('status')
    if status_filter:
        payments = payments.filter(status=status_filter)
    
    query = request.GET.get('q')
    if query:
        payments = payments.filter(
            Q(member__user__first_name__icontains=query) |
            Q(member__user__last_name__icontains=query) |
            Q(transaction_ref__icontains=query) |
            Q(external_ref__icontains=query)
        )
    
    paginator = Paginator(payments, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'title': 'Payments',
        'payments': page_obj,
        'status_filter': status_filter,
        'query': query,
    }
    return render(request, 'finance/payments/list.html', context)


@login_required
def payment_detail(request, payment_id):
    """View payment details"""
    payment = get_object_or_404(Payment, id=payment_id)
    
    if not request.user.is_admin and not request.user.is_superuser:
        try:
            member = Member.objects.get(user=request.user)
            if payment.member != member:
                messages.error(request, 'You do not have permission to view this payment.')
                return redirect('finance:payment_list')
        except Member.DoesNotExist:
            messages.error(request, 'You are not registered as a member.')
            return redirect('finance:payment_list')
    
    context = {
        'title': f'Payment #{payment.id}',
        'payment': payment,
    }
    return render(request, 'finance/payments/detail.html', context)


@login_required
@admin_required
def payment_approve(request, payment_id):
    """Approve a pending payment - Admin only"""
    payment = get_object_or_404(Payment, id=payment_id)
    
    if payment.status != 'pending':
        messages.warning(request, 'This payment is not pending.')
        return redirect('finance:payment_detail', payment_id=payment.id)
    
    if request.method == 'POST':
        payment.verify(request.user)
        messages.success(request, f'Payment #{payment.id} approved successfully!')
        return redirect('finance:payment_detail', payment_id=payment.id)
    
    context = {
        'title': f'Approve Payment #{payment.id}',
        'payment': payment,
    }
    return render(request, 'finance/payments/approve.html', context)


@login_required
def payment_history(request):
    """View payment history with pagination"""
    payments = Payment.objects.filter(status='completed').order_by('-created_at')
    
    # Regular users only see their own payments
    if not request.user.is_admin and not request.user.is_superuser:
        try:
            member = Member.objects.get(user=request.user)
            payments = payments.filter(member=member)
        except Member.DoesNotExist:
            payments = Payment.objects.none()
    
    # Date range filters
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
    if start_date:
        payments = payments.filter(created_at__date__gte=start_date)
    if end_date:
        payments = payments.filter(created_at__date__lte=end_date)
    
    # Calculate totals BEFORE pagination
    total_amount = payments.aggregate(total=Sum('amount'))['total'] or 0
    total_count = payments.count()
    
    # Pagination - 15 items per page
    paginator = Paginator(payments, 15)
    page = request.GET.get('page')
    
    try:
        payments_page = paginator.page(page)
    except PageNotAnInteger:
        payments_page = paginator.page(1)
    except EmptyPage:
        payments_page = paginator.page(paginator.num_pages)
    
    context = {
        'title': 'Payment History',
        'payments': payments_page,
        'total_amount': total_amount,
        'total_count': total_count,
        'start_date': start_date,
        'end_date': end_date,
        'paginator': paginator,
        'page_obj': payments_page,
        'start_index': (payments_page.number - 1) * 15 + 1,
        'end_index': min(payments_page.number * 15, total_count),
    }
    return render(request, 'finance/payments/history.html', context)


@login_required
def receipt_view(request, payment_id):
    """View payment receipt"""
    payment = get_object_or_404(Payment, id=payment_id)
    
    if not request.user.is_admin and not request.user.is_superuser:
        try:
            member = Member.objects.get(user=request.user)
            if payment.member != member:
                messages.error(request, 'You do not have permission to view this receipt.')
                return redirect('finance:payment_list')
        except Member.DoesNotExist:
            messages.error(request, 'You are not registered as a member.')
            return redirect('finance:payment_list')
    
    try:
        receipt = PaymentReceipt.objects.get(payment=payment)
    except PaymentReceipt.DoesNotExist:
        from finance.services import FinanceService
        receipt = FinanceService.generate_receipt(payment)
    
    context = {
        'title': f'Receipt #{receipt.receipt_number}',
        'receipt': receipt,
        'payment': payment,
    }
    return render(request, 'finance/receipts/view.html', context)


@login_required
def receipt_download(request, payment_id):
    """Download payment receipt"""
    payment = get_object_or_404(Payment, id=payment_id)
    
    if not request.user.is_admin and not request.user.is_superuser:
        try:
            member = Member.objects.get(user=request.user)
            if payment.member != member:
                messages.error(request, 'You do not have permission to download this receipt.')
                return redirect('finance:payment_list')
        except Member.DoesNotExist:
            messages.error(request, 'You are not registered as a member.')
            return redirect('finance:payment_list')
    
    try:
        receipt = PaymentReceipt.objects.get(payment=payment)
    except PaymentReceipt.DoesNotExist:
        from finance.services import FinanceService
        receipt = FinanceService.generate_receipt(payment)
    
    if receipt.pdf_file:
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="receipt_{receipt.receipt_number}.pdf"'
        response.write(receipt.pdf_file.read())
        return response
    
    context = {
        'receipt': receipt,
        'payment': payment,
    }
    return render(request, 'finance/receipts/download.html', context)


@login_required
def send_reminder(request, member_id=None):
    """Send payment reminder to member(s)"""
    if not request.user.is_treasurer and not request.user.is_admin:
        messages.error(request, 'Only treasurer or admin can send reminders.')
        return redirect('dashboard:index')
    
    if request.method == 'POST':
        member_id = request.POST.get('member_id')
        category_id = request.POST.get('category_id')
        message = request.POST.get('message')
        
        member = get_object_or_404(Member, member_id=member_id)
        category = None
        if category_id:
            category = get_object_or_404(PaymentCategory, id=category_id)
        
        reminder = PaymentReminder.objects.create(
            member=member,
            category=category,
            reminder_type='manual',
            message=message or f'Please make your payment for {category.name if category else "due payments"}.',
            sent_by=request.user
        )
        
        messages.success(request, f'Reminder sent to {member.get_full_name()}')
        return redirect('finance:payment_list')
    
    members = Member.objects.filter(status='active')
    categories = PaymentCategory.objects.filter(is_active=True)
    
    context = {
        'title': 'Send Payment Reminder',
        'members': members,
        'categories': categories,
        'selected_member': member_id,
    }
    return render(request, 'finance/send_reminder.html', context)


@login_required
def get_member_payments_json(request, member_id):
    """Get member payments as JSON for API"""
    try:
        member = Member.objects.get(member_id=member_id)
    except Member.DoesNotExist:
        return JsonResponse({'error': 'Member not found'}, status=404)
    
    if not request.user.is_admin and not request.user.is_superuser:
        try:
            current_member = Member.objects.get(user=request.user)
            if current_member != member:
                return JsonResponse({'error': 'Permission denied'}, status=403)
        except Member.DoesNotExist:
            return JsonResponse({'error': 'Not a member'}, status=403)
    
    payments = Payment.objects.filter(
        member=member,
        status='completed'
    ).values('category__name', 'amount', 'created_at')
    
    total = Payment.objects.filter(member=member, status='completed').aggregate(
        total=Sum('amount')
    )['total'] or 0
    
    data = {
        'member_id': member.member_id,
        'name': member.get_full_name(),
        'total_paid': float(total),
        'payments': list(payments),
    }
    return JsonResponse(data)


@login_required
def get_category_stats_json(request):
    """Get category statistics as JSON"""
    categories = PaymentCategory.objects.filter(is_active=True)
    stats = []
    
    for category in categories:
        total = Payment.objects.filter(
            category=category,
            status='completed'
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        count = Payment.objects.filter(
            category=category,
            status='completed'
        ).count()
        
        stats.append({
            'id': category.id,
            'name': category.name,
            'total': float(total),
            'count': count,
            'color': category.color,
        })
    
    return JsonResponse({'categories': stats})
