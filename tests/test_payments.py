"""
Payments Tests for LakChogo Connect
"""

from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from members.models import Member
from finance.models import PaymentCategory, Payment, PaymentReceipt

User = get_user_model()

class PaymentCategoryTest(TestCase):
    """Test PaymentCategory model"""

    def setUp(self):
        """Set up test data"""
        self.category = PaymentCategory.objects.create(
            name='Yearly Subscription',
            description='Annual membership fee',
            default_amount=500,
            frequency='yearly',
            is_mandatory_for_welfare=True,
            is_active=True
        )

    def test_category_creation(self):
        """Test category creation"""
        self.assertEqual(self.category.name, 'Yearly Subscription')
        self.assertEqual(self.category.default_amount, 500)
        self.assertTrue(self.category.is_mandatory_for_welfare)
        self.assertTrue(self.category.is_active)

    def test_category_str(self):
        """Test category string representation"""
        self.assertEqual(str(self.category), 'Yearly Subscription (KES 500)')

class PaymentTest(TestCase):
    """Test Payment model"""

    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username='testuser',
            phone='+254712345678',
            password='TestPass123'
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
        """Test payment creation"""
        self.assertEqual(self.payment.amount, 200)
        self.assertEqual(self.payment.status, 'completed')
        self.assertEqual(self.payment.payment_method, 'cash')

    def test_payment_str(self):
        """Test payment string representation"""
        self.assertIn('testuser', str(self.payment))
        self.assertIn('Emergency Fund', str(self.payment))

    def test_payment_verify(self):
        """Test payment verification"""
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
        """Test payment cancellation"""
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
        """Test payment refund"""
        payment = Payment.objects.create(
            member=self.member,
            category=self.category,
            amount=100,
            payment_method='mpesa',
            status='completed'
        )
        payment.refund()
        self.assertEqual(payment.status, 'refunded')

    def test_payment_properties(self):
        """Test payment properties"""
        payment = Payment.objects.create(
            member=self.member,
            category=self.category,
            amount=100,
            payment_method='mpesa',
            status='pending'
        )
        self.assertTrue(payment.is_pending)
        self.assertFalse(payment.is_completed)

class PaymentViewsTest(TestCase):
    """Test Payment views"""

    def setUp(self):
        """Set up test data"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            phone='+254712345678',
            password='TestPass123'
        )
        self.member = Member.objects.create(user=self.user, status='active')
        self.category = PaymentCategory.objects.create(
            name='Test Category',
            default_amount=100
        )
        self.client.login(username='testuser', password='TestPass123')

    def test_finance_index(self):
        """Test finance index view"""
        response = self.client.get(reverse('finance:index'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'finance/index.html')

    def test_category_list(self):
        """Test category list view"""
        response = self.client.get(reverse('finance:category_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'finance/categories/list.html')

    def test_record_payment(self):
        """Test record payment view"""
        response = self.client.get(reverse('finance:record_payment'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'finance/record_payment.html')

    def test_payment_list(self):
        """Test payment list view"""
        response = self.client.get(reverse('finance:payment_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'finance/payments/list.html')

    def test_payment_detail(self):
        """Test payment detail view"""
        payment = Payment.objects.create(
            member=self.member,
            category=self.category,
            amount=100,
            payment_method='cash',
            status='completed',
            recorded_by=self.user
        )
        response = self.client.get(reverse('finance:payment_detail', args=[payment.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'finance/payments/detail.html')
