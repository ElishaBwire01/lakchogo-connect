from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Payment, PaymentCategory

@login_required
def index(request):
    """Finance dashboard"""
    context = {
        'title': 'Finance',
        'total_payments': Payment.objects.filter(status='completed').count(),
        'pending_payments': Payment.objects.filter(status='pending').count(),
    }
    return render(request, 'finance/index.html', context)

@login_required
def record_payment(request):
    """Record a new payment"""
    categories = PaymentCategory.objects.filter(is_active=True)
    
    if request.method == 'POST':
        # Process payment form
        member_id = request.POST.get('member_id')
        category_id = request.POST.get('category_id')
        amount = request.POST.get('amount')
        payment_method = request.POST.get('payment_method')
        
        # Create payment record
        from members.models import Member
        member = get_object_or_404(Member, member_id=member_id)
        category = get_object_or_404(PaymentCategory, id=category_id)
        
        payment = Payment.objects.create(
            member=member,
            category=category,
            amount=amount,
            payment_method=payment_method,
            status='completed',
            recorded_by=request.user,
            notes=request.POST.get('notes', '')
        )
        
        messages.success(request, f'Payment of KES {amount} recorded for {member.get_full_name()}')
        return redirect('finance:payment_list')
    
    context = {
        'title': 'Record Payment',
        'categories': categories,
    }
    return render(request, 'finance/record_payment.html', context)

@login_required
def payment_list(request):
    """List all payments"""
    payments = Payment.objects.all().order_by('-created_at')
    context = {
        'title': 'Payments',
        'payments': payments,
    }
    return render(request, 'finance/payment_list.html', context)

@login_required
def payment_detail(request, payment_id):
    """View payment details"""
    payment = get_object_or_404(Payment, id=payment_id)
    context = {
        'title': 'Payment Detail',
        'payment': payment,
    }
    return render(request, 'finance/payment_detail.html', context)

@login_required
def category_list(request):
    """List payment categories"""
    categories = PaymentCategory.objects.filter(is_active=True)
    context = {
        'title': 'Payment Categories',
        'categories': categories,
    }
    return render(request, 'finance/category_list.html', context)
