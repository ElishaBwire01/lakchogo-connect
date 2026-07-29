from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from .models import BereavementEvent, BereavementContribution, WelfareFund
from members.models import Member

User = get_user_model()

class BereavementEventTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            phone='+254712345678',
            password='TestPassword123'
        )
        self.member = Member.objects.create(user=self.user)
        self.event = BereavementEvent.objects.create(
            member=self.member,
            deceased_name='John Doe',
            relationship='Father',
            date_of_death=timezone.now().date(),
            collection_target=50000,
            status='active'
        )
    
    def test_event_creation(self):
        self.assertEqual(self.event.deceased_name, 'John Doe')
        self.assertEqual(self.event.collection_target, 50000)
        self.assertEqual(self.event.status, 'active')
        self.assertIsNotNone(self.event.event_code)
    
    def test_progress_percentage(self):
        self.assertEqual(self.event.progress_percentage, 0)
        self.event.amount_collected = 25000
        self.event.save()
        self.assertEqual(self.event.progress_percentage, 50)
    
    def test_is_fully_collected(self):
        self.assertFalse(self.event.is_fully_collected)
        self.event.amount_collected = 50000
        self.event.save()
        self.assertTrue(self.event.is_fully_collected)
    
    def test_close_event(self):
        self.event.close()
        self.assertEqual(self.event.status, 'closed')
    
    def test_event_str(self):
        self.assertIn('John Doe', str(self.event))

class BereavementContributionTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            phone='+254712345678',
            password='TestPassword123'
        )
        self.member = Member.objects.create(user=self.user)
        self.event = BereavementEvent.objects.create(
            member=self.member,
            deceased_name='John Doe',
            relationship='Father',
            date_of_death=timezone.now().date(),
            collection_target=50000
        )
        self.contribution = BereavementContribution.objects.create(
            event=self.event,
            contributor=self.member,
            amount=1000,
            payment_method='cash'
        )
    
    def test_contribution_creation(self):
        self.assertEqual(self.contribution.amount, 1000)
        self.assertEqual(self.contribution.event, self.event)
        self.assertEqual(self.contribution.contributor, self.member)
    
    def test_contribution_updates_event(self):
        self.assertEqual(self.event.amount_collected, 1000)
    
    def test_contribution_str(self):
        self.assertIn('1000', str(self.contribution))

class WelfareFundTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            phone='+254712345678',
            password='TestPassword123'
        )
        self.fund = WelfareFund.objects.create(
            name='General Fund',
            fund_type='general',
            balance=10000,
            created_by=self.user
        )
    
    def test_fund_creation(self):
        self.assertEqual(self.fund.name, 'General Fund')
        self.assertEqual(self.fund.balance, 10000)
    
    def test_add_funds(self):
        self.fund.add_funds(5000, 'Test deposit', self.user)
        self.assertEqual(self.fund.balance, 15000)
    
    def test_deduct_funds(self):
        result = self.fund.deduct_funds(5000, 'Test withdrawal', self.user)
        self.assertEqual(result, 5000)
        self.assertEqual(self.fund.balance, 5000)
    
    def test_deduct_funds_insufficient(self):
        result = self.fund.deduct_funds(20000, 'Test withdrawal', self.user)
        self.assertIsNone(result)
