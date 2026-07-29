"""
API Tests for LakChogo Connect
"""

from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from members.models import Member
from finance.models import PaymentCategory, Payment

User = get_user_model()

class APITest(TestCase):
    """Test API endpoints"""

    def setUp(self):
        """Set up test data"""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            phone='+254712345678',
            password='TestPass123',
            first_name='Test',
            last_name='User'
        )
        self.member = Member.objects.create(user=self.user, status='active')
        self.client.force_authenticate(user=self.user)

    def test_member_api(self):
        """Test member API endpoint"""
        response = self.client.get(reverse('members:api_member', args=[self.member.member_id]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['member_id'], self.member.member_id)

    def test_members_api_all(self):
        """Test members API all endpoint"""
        response = self.client.get(reverse('members:api_all'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('members', response.data)

    def test_payment_member_api(self):
        """Test payment member API endpoint"""
        category = PaymentCategory.objects.create(name='Test Category', default_amount=100)
        payment = Payment.objects.create(
            member=self.member,
            category=category,
            amount=100,
            payment_method='cash',
            status='completed'
        )
        response = self.client.get(reverse('finance:member_payments_json', args=[self.member.member_id]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['member_id'], self.member.member_id)

    def test_compliance_stats_api(self):
        """Test compliance stats API endpoint"""
        response = self.client.get(reverse('compliance:stats_json'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('total', response.data)

    def test_meeting_summary_api(self):
        """Test meeting summary API endpoint"""
        from meetings.models import Meeting
        meeting = Meeting.objects.create(
            title='Test Meeting',
            date=timezone.now(),
            venue='Test Venue',
            created_by=self.user
        )
        response = self.client.get(reverse('meetings:summary', args=[meeting.id]))
        self.assertEqual(response.status_code, 200)
        self.assertIn('meeting_id', response.data)

    def test_unauthenticated_api(self):
        """Test unauthenticated API access"""
        client = APIClient()
        response = client.get(reverse('members:api_all'))
        self.assertEqual(response.status_code, 401)

    def test_check_username_api(self):
        """Test check username API"""
        response = self.client.get(reverse('accounts:check_username') + '?username=testuser')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data['exists'])

        response = self.client.get(reverse('accounts:check_username') + '?username=newname')
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.data['exists'])
