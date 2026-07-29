from django.test import TestCase
from django.contrib.auth import get_user_model
from .models import PaymentCategory, Payment
from members.models import Member

User = get_user_model()

class PaymentCategoryTest(TestCase):
    def setUp(self):
        self.category = PaymentCategory.objects.create(
            name='Yearly Subscription',
            description='Annual membership fee',
            default_amount=500,
            frequency='yearly',
            is_mandatory_for_welfare=True,
            is_active=True
        )
    
    def test_category_creation(self):
        self.assertEqual(self.category.name, 'Yearly Subscription')
        self.assertEqual(self.category.default_amount, 500)
        self.assertTrue(self.category.is_mandatory_for_welfare)
        self.assertTrue(self.category.is_active)
    
    def test_category_str(self):
        self.assertEqual(str(self.category), 'Yearly Subscription (KES 500)')

class PaymentTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            phone='+254712345678',
            password='TestPassword123'
        )
        self.member = Member.objects.create(
            user=self.user,
            status='active'
        )
        self.category = PaymentCategory.objects.create(
            name='Emergency Fund',
            default_amount=200
        )
        self.payment = Payment.objects.create(
            member=self.member,
            category=self.category,
            amount=200,
            payment_method='cash',
            status='completed',
            recorded_by=self.user,
            verified_by=self.user
        )
    
    def test_payment_creation(self):
        self.assertEqual(self.payment.amount, 200)
        self.assertEqual(self.payment.status, 'completed')
        self.assertEqual(self.payment.payment_method, 'cash')
    
    def test_payment_str(self):
        self.assertIn('testuser', str(self.payment))
        self.assertIn('Emergency Fund', str(self.payment))
    
    def test_payment_verify(self):
        payment = Payment.objects.create(
            member=self.member,
            category=self.category,
            amount=100,
            payment_method='mpesa',
            status='pending'
        )
        payment.verify(self.user)
        self.assertEqual(payment.status, 'completed')
        self.assertEqual(payment.verified_by, self.user)
    
    def test_payment_cancel(self):
        payment = Payment.objects.create(
            member=self.member,
            category=self.category,
            amount=100,
            payment_method='mpesa',
            status='pending'
        )
        payment.cancel()
        self.assertEqual(payment.status, 'cancelled')
    
    def test_payment_refund(self):
        payment = Payment.objects.create(
            member=self.member,
            category=self.category,
            amount=100,
            payment_method='mpesa',
            status='completed'
        )
        payment.refund()
        self.assertEqual(payment.status, 'refunded')
