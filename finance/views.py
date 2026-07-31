from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.http import JsonResponse, HttpResponse
from django.db.models import Sum, Count, Q
from django.utils import timezone
from datetime import datetime, timedelta
from .models import PaymentCategory, Payment, PaymentReceipt, PaymentReminder
from members.models import Member

@login_required
def index(request):
    """Finance dashboard"""
    # Stats
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
def category_create(request):
    """Create a new payment category"""
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
def category_edit(request, category_id):
    """Edit a payment category"""
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
    """Record a new payment"""
    members = Member.objects.filter(status='active')
    categories = PaymentCategory.objects.filter(is_active=True)
    
    if request.method == 'POST':
        member_id = request.POST.get('member_id')
        category_id = request.POST.get('category_id')
        amount = request.POST.get('amount')
        payment_method = request.POST.get('payment_method')
        transaction_ref = request.POST.get('transaction_ref')
        notes = request.POST.get('notes')
        
        if not all([member_id, category_id, amount]):
            messages.error(request, 'Please fill in all required fields.')
            return render(request, 'finance/record_payment.html', {
                'members': members,
                'categories': categories,
                'title': 'Record Payment',
            })
        
        member = get_object_or_404(Member, member_id=member_id)
        category = get_object_or_404(PaymentCategory, id=category_id)
        
        payment = Payment.objects.create(
            member=member,
            category=category,
            amount=amount,
            payment_method=payment_method or 'cash',
            transaction_ref=transaction_ref or '',
            status='completed',
            recorded_by=request.user,
            verified_by=request.user,
            verified_at=timezone.now(),
            notes=notes or ''
        )
        
        messages.success(request, f'Payment of KES {amount} recorded for {member.get_full_name()}')
        return redirect('finance:payment_detail', payment_id=payment.id)
    
    context = {
        'title': 'Record Payment',
        'members': members,
        'categories': categories,
    }
    return render(request, 'finance/record_payment.html', context)


@login_required
def payment_list(request):
    """List all payments"""
    payments = Payment.objects.all().order_by('-created_at')
    
    # Filters
    status_filter = request.GET.get('status')
    if status_filter:
        payments = payments.filter(status=status_filter)
    
    member_filter = request.GET.get('member')
    if member_filter:
        payments = payments.filter(member__member_id=member_filter)
    
    category_filter = request.GET.get('category')
    if category_filter:
        payments = payments.filter(category__id=category_filter)
    
    # Search
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
        'member_filter': member_filter,
        'category_filter': category_filter,
        'query': query,
    }
    return render(request, 'finance/payments/list.html', context)


@login_required
def payment_detail(request, payment_id):
    """View payment details"""
    payment = get_object_or_404(Payment, id=payment_id)
    
    context = {
        'title': f'Payment #{payment.id}',
        'payment': payment,
    }
    return render(request, 'finance/payments/detail.html', context)


@login_required
def payment_approve(request, payment_id):
    """Approve a pending payment"""
    payment = get_object_or_404(Payment, id=payment_id)
    
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
    """View payment history with filters"""
    payments = Payment.objects.filter(status='completed').order_by('-created_at')
    
    # Date range filter
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
    if start_date:
        payments = payments.filter(created_at__date__gte=start_date)
    if end_date:
        payments = payments.filter(created_at__date__lte=end_date)
    
    # Summary
    total_amount = payments.aggregate(total=Sum('amount'))['total'] or 0
    total_count = payments.count()
    
    context = {
        'title': 'Payment History',
        'payments': payments[:100],
        'total_amount': total_amount,
        'total_count': total_count,
        'start_date': start_date,
        'end_date': end_date,
    }
    return render(request, 'finance/payments/history.html', context)


@login_required
def receipt_view(request, payment_id):
    """View payment receipt"""
    payment = get_object_or_404(Payment, id=payment_id)
    receipt = get_object_or_404(PaymentReceipt, payment=payment)
    
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
    receipt = get_object_or_404(PaymentReceipt, payment=payment)
    
    if receipt.pdf_file:
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="receipt_{receipt.receipt_number}.pdf"'
        response.write(receipt.pdf_file.read())
        return response
    
    messages.error(request, 'No PDF file available for this receipt.')
    return redirect('finance:receipt_view', payment_id=payment.id)


@login_required
def send_reminder(request, member_id=None):
    """Send payment reminder to member(s)"""
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
    member = get_object_or_404(Member, member_id=member_id)
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

@login_required
def receipt_view(request, payment_id):
    """View payment receipt"""
    payment = get_object_or_404(Payment, id=payment_id)
    try:
        receipt = PaymentReceipt.objects.get(payment=payment)
    except PaymentReceipt.DoesNotExist:
        # Generate receipt if not exists
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
    
    # If no PDF, generate HTML receipt
    context = {
        'receipt': receipt,
        'payment': payment,
    }
    return render(request, 'finance/receipts/download.html', context)
