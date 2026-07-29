from django.test import TestCase
from django.contrib.auth import get_user_model
from .models import ComplianceRule, ComplianceScore, ComplianceAlert
from members.models import Member
from finance.models import PaymentCategory, Payment

User = get_user_model()

class ComplianceRuleTest(TestCase):
    def setUp(self):
        self.rule = ComplianceRule.objects.create(
            name='Test Rule',
            description='Test description',
            rule_type='payment',
            grace_period_days=30,
            penalty_points=10,
            is_active=True
        )
    
    def test_rule_creation(self):
        self.assertEqual(self.rule.name, 'Test Rule')
        self.assertEqual(self.rule.penalty_points, 10)
        self.assertTrue(self.rule.is_active)
    
    def test_rule_str(self):
        self.assertEqual(str(self.rule), 'Test Rule (Payment)')

class ComplianceScoreTest(TestCase):
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
        self.score = ComplianceScore.objects.create(
            member=self.member,
            status='green',
            score=100,
            payment_compliance=100,
            attendance_compliance=100
        )
    
    def test_score_creation(self):
        self.assertEqual(self.score.status, 'green')
        self.assertEqual(self.score.score, 100)
        self.assertTrue(self.score.is_eligible)
    
    def test_update_status(self):
        self.score.score = 50
        self.score.update_status()
        self.assertEqual(self.score.status, 'red')
        self.assertFalse(self.score.is_eligible)
    
    def test_score_str(self):
        self.assertIn('testuser', str(self.score))

class ComplianceAlertTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            phone='+254712345678',
            password='TestPassword123'
        )
        self.member = Member.objects.create(user=self.user)
        self.alert = ComplianceAlert.objects.create(
            member=self.member,
            alert_type='compliance_low',
            priority='high',
            message='Test alert message'
        )
    
    def test_alert_creation(self):
        self.assertEqual(self.alert.message, 'Test alert message')
        self.assertEqual(self.alert.priority, 'high')
        self.assertFalse(self.alert.is_resolved)
    
    def test_resolve_alert(self):
        self.alert.resolve(self.user, 'Test resolution')
        self.assertTrue(self.alert.is_resolved)
        self.assertIsNotNone(self.alert.resolved_at)
        self.assertEqual(self.alert.resolved_by, self.user)
    
    def test_alert_str(self):
        self.assertIn('testuser', str(self.alert))
