from django.db.models import Sum, Count, Q
from django.utils import timezone
from datetime import datetime, timedelta
from .models import Payment, PaymentCategory, PaymentReceipt, PaymentReminder
from members.models import Member

class FinanceService:
    """Service layer for finance operations"""
    
    @staticmethod
    def get_payment_summary():
        """Get payment summary statistics"""
        total = Payment.objects.filter(status='completed').aggregate(
            total=Sum('amount')
        )['total'] or 0
        
        monthly = Payment.objects.filter(
            status='completed',
            created_at__gte=timezone.now() - timedelta(days=30)
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        pending = Payment.objects.filter(status='pending').count()
        
        return {
            'total': total,
            'monthly': monthly,
            'pending': pending,
            'count': Payment.objects.filter(status='completed').count(),
        }
    
    @staticmethod
    def get_member_payments(member_id):
        """Get all payments for a member"""
        member = Member.objects.get(member_id=member_id)
        payments = Payment.objects.filter(
            member=member,
            status='completed'
        ).select_related('category')
        
        total = payments.aggregate(total=Sum('amount'))['total'] or 0
        
        return {
            'member': member,
            'payments': payments,
            'total': total,
            'count': payments.count(),
        }
    
    @staticmethod
    def get_category_stats():
        """Get statistics per category"""
        categories = PaymentCategory.objects.filter(is_active=True)
        stats = []
        
        for category in categories:
            payments = Payment.objects.filter(
                category=category,
                status='completed'
            )
            stats.append({
                'category': category,
                'total': payments.aggregate(total=Sum('amount'))['total'] or 0,
                'count': payments.count(),
            })
        
        return stats
    
    @staticmethod
    def generate_receipt(payment):
        """Generate a receipt for a payment"""
        import random
        import string
        
        # Generate receipt number
        receipt_number = f"REC-{payment.id}-{''.join(random.choices(string.digits, k=6))}"
        
        receipt, created = PaymentReceipt.objects.get_or_create(
            payment=payment,
            defaults={
                'receipt_number': receipt_number,
                'generated_by': payment.recorded_by,
            }
        )
        
        if not created:
            receipt.receipt_number = receipt_number
            receipt.save()
        
        return receipt
    
    @staticmethod
    def get_overdue_members():
        """Get members with overdue payments"""
        # This would check payment categories and last payment dates
        members = Member.objects.filter(status='active')
        overdue = []
        
        for member in members:
            categories = PaymentCategory.objects.filter(is_active=True)
            for category in categories:
                last_payment = Payment.objects.filter(
                    member=member,
                    category=category,
                    status='completed'
                ).order_by('-created_at').first()
                
                if not last_payment:
                    overdue.append({
                        'member': member,
                        'category': category,
                        'days_overdue': 30,  # Default
                    })
                elif last_payment.created_at < timezone.now() - timedelta(days=30):
                    days = (timezone.now() - last_payment.created_at).days
                    overdue.append({
                        'member': member,
                        'category': category,
                        'days_overdue': days,
                    })
        
        return overdue
    
    @staticmethod
    def get_member_balance(member_id):
        """Get member's balance"""
        member = Member.objects.get(member_id=member_id)
        
        paid = Payment.objects.filter(
            member=member,
            status='completed'
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        # Calculate expected based on categories
        categories = PaymentCategory.objects.filter(is_active=True)
        expected = sum([cat.default_amount for cat in categories])
        
        return {
            'member': member,
            'paid': paid,
            'expected': expected,
            'balance': expected - paid,
        }
    
    @staticmethod
    def get_monthly_trend(months=12):
        """Get monthly payment trend"""
        trend = []
        now = timezone.now()
        
        for i in range(months):
            month_start = now.replace(day=1) - timedelta(days=30*i)
            month_end = month_start + timedelta(days=30)
            
            total = Payment.objects.filter(
                status='completed',
                created_at__gte=month_start,
                created_at__lt=month_end
            ).aggregate(total=Sum('amount'))['total'] or 0
            
            trend.append({
                'month': month_start.strftime('%b %Y'),
                'total': total,
            })
        
        return reversed(trend)
