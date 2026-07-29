"""
Authentication Tests for LakChogo Connect
"""

from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.contrib.messages import get_messages

User = get_user_model()

class AuthenticationTest(TestCase):
    """Test user authentication"""

    def setUp(self):
        """Set up test data"""
        self.client = Client()
        self.user_data = {
            'username': 'testuser',
            'password': 'TestPass123',
            'first_name': 'Test',
            'last_name': 'User',
            'phone': '+254712345678',
            'id_number': '12345678',
            'email': 'test@example.com'
        }
        self.user = User.objects.create_user(**self.user_data)
        self.login_url = reverse('accounts:login')
        self.register_url = reverse('accounts:register')
        self.dashboard_url = reverse('dashboard:index')
        self.profile_url = reverse('accounts:profile')

    def test_user_registration(self):
        """Test user registration"""
        response = self.client.get(self.register_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/register.html')

    def test_user_login(self):
        """Test user login"""
        response = self.client.post(self.login_url, {
            'username': 'testuser',
            'password': 'TestPass123'
        })
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, self.dashboard_url)

    def test_login_required(self):
        """Test login required for protected pages"""
        response = self.client.get(self.dashboard_url)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith(self.login_url))

    def test_invalid_login(self):
        """Test login with invalid credentials"""
        response = self.client.post(self.login_url, {
            'username': 'testuser',
            'password': 'WrongPassword'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Invalid username or password')

    def test_user_logout(self):
        """Test user logout"""
        self.client.login(username='testuser', password='TestPass123')
        response = self.client.get(reverse('accounts:logout'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('accounts:login'))

    def test_profile_access(self):
        """Test profile page access"""
        self.client.login(username='testuser', password='TestPass123')
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/profile.html')

    def test_profile_edit(self):
        """Test profile editing"""
        self.client.login(username='testuser', password='TestPass123')
        response = self.client.get(reverse('accounts:profile_edit'))
        self.assertEqual(response.status_code, 200)

    def test_password_reset(self):
        """Test password reset page"""
        response = self.client.get(reverse('accounts:password_reset'))
        self.assertEqual(response.status_code, 200)

    def test_registration_with_existing_username(self):
        """Test registration with existing username"""
        response = self.client.post(self.register_url, {
            'username': 'testuser',
            'password1': 'NewPass123',
            'password2': 'NewPass123',
            'first_name': 'Test',
            'last_name': 'User',
            'phone': '+254798765432',
            'id_number': '87654321'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Username already exists')

    def test_registration_password_mismatch(self):
        """Test registration with password mismatch"""
        response = self.client.post(self.register_url, {
            'username': 'newuser',
            'password1': 'Pass1234',
            'password2': 'Pass5678',
            'first_name': 'New',
            'last_name': 'User',
            'phone': '+254798765432',
            'id_number': '87654321'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Passwords do not match')
