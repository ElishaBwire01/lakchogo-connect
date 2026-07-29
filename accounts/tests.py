from django.test import TestCase
from django.contrib.auth import get_user_model
from .models import Role, UserRole, UserActivityLog

User = get_user_model()

class UserModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            phone='+254712345678',
            password='TestPassword123',
            first_name='Test',
            last_name='User',
            id_number='12345678'
        )
    
    def test_user_creation(self):
        self.assertEqual(self.user.username, 'testuser')
        self.assertEqual(self.user.phone, '+254712345678')
        self.assertTrue(self.user.check_password('TestPassword123'))
        self.assertEqual(self.user.get_full_name(), 'Test User')
        self.assertEqual(self.user.id_number, '12345678')
    
    def test_user_str_method(self):
        self.assertEqual(str(self.user), 'Test User (+254712345678)')

class RoleModelTest(TestCase):
    def setUp(self):
        self.role = Role.objects.create(
            name='Admin',
            description='Administrator role',
            is_default=False
        )
    
    def test_role_creation(self):
        self.assertEqual(self.role.name, 'Admin')
        self.assertEqual(self.role.description, 'Administrator role')
        self.assertFalse(self.role.is_default)
    
    def test_role_str_method(self):
        self.assertEqual(str(self.role), 'Admin')

class UserRoleModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            phone='+254712345678',
            password='TestPassword123'
        )
        self.role = Role.objects.create(name='Member')
        self.user_role = UserRole.objects.create(
            user=self.user,
            role=self.role
        )
    
    def test_user_role_creation(self):
        self.assertEqual(self.user_role.user, self.user)
        self.assertEqual(self.user_role.role, self.role)
        self.assertTrue(self.user_role.is_active)
    
    def test_user_role_str(self):
        self.assertEqual(str(self.user_role), 'testuser - Member')

class UserActivityLogTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            phone='+254712345678',
            password='TestPassword123'
        )
        self.log = UserActivityLog.objects.create(
            user=self.user,
            action='LOGIN',
            description='User logged in'
        )
    
    def test_log_creation(self):
        self.assertEqual(self.log.user, self.user)
        self.assertEqual(self.log.action, 'LOGIN')
        self.assertEqual(self.log.description, 'User logged in')
    
    def test_log_str(self):
        self.assertIn('testuser', str(self.log))
