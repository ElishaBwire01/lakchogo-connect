"""
Compliance Tests for LakChogo Connect
"""

from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from members.models import Member
from compliance.models import ComplianceRule, ComplianceScore, ComplianceAlert

User = get_user_model()

class ComplianceRuleTest(TestCase):
    """Test ComplianceRule model"""

    def setUp(self):
        """Set up test data"""
        self.rule = ComplianceRule.objects.create(
            name='Test Rule',
            description='Test description',
            rule_type='payment',
            grace_period_days=30,
            penalty_points=10,
            is_active=True
        )

    def test_rule_creation(self):
        """Test rule creation"""
        self.assertEqual(self.rule.name, 'Test Rule')
        self.assertEqual(self.rule.penalty_points, 10)
        self.assertTrue(self.rule.is_active)

    def test_rule_str(self):
        """Test rule string representation"""
        self.assertEqual(str(self.rule), 'Test Rule (Payment)')

class ComplianceScoreTest(TestCase):
    """Test ComplianceScore model"""

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
        self.score = ComplianceScore.objects.create(
            member=self.member,
            status='green',
            score=100,
            payment_compliance=100,
            attendance_compliance=100
        )

    def test_score_creation(self):
        """Test score creation"""
        self.assertEqual(self.score.status, 'green')
        self.assertEqual(self.score.score, 100)
        self.assertTrue(self.score.is_eligible)

    def test_update_status(self):
        """Test update status"""
        self.score.score = 50
        self.score.update_status()
        self.assertEqual(self.score.status, 'red')
        self.assertFalse(self.score.is_eligible)

    def test_score_str(self):
        """Test score string representation"""
        self.assertIn('testuser', str(self.score))

class ComplianceAlertTest(TestCase):
    """Test ComplianceAlert model"""

    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username='testuser',
            phone='+254712345678',
            password='TestPass123'
        )
        self.member = Member.objects.create(user=self.user)
        self.alert = ComplianceAlert.objects.create(
            member=self.member,
            alert_type='compliance_low',
            priority='high',
            message='Test alert message'
        )

    def test_alert_creation(self):
        """Test alert creation"""
        self.assertEqual(self.alert.message, 'Test alert message')
        self.assertEqual(self.alert.priority, 'high')
        self.assertFalse(self.alert.is_resolved)

    def test_resolve_alert(self):
        """Test resolve alert"""
        self.alert.resolve(self.user, 'Test resolution')
        self.assertTrue(self.alert.is_resolved)
        self.assertIsNotNone(self.alert.resolved_at)
        self.assertEqual(self.alert.resolved_by, self.user)

    def test_alert_str(self):
        """Test alert string representation"""
        self.assertIn('testuser', str(self.alert))

class ComplianceViewsTest(TestCase):
    """Test Compliance views"""

    def setUp(self):
        """Set up test data"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            phone='+254712345678',
            password='TestPass123'
        )
        self.member = Member.objects.create(user=self.user, status='active')
        self.client.login(username='testuser', password='TestPass123')

    def test_compliance_index(self):
        """Test compliance index view"""
        response = self.client.get(reverse('compliance:index'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'compliance/index.html')

    def test_compliance_scorecard(self):
        """Test compliance scorecard view"""
        response = self.client.get(reverse('compliance:scorecard'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'compliance/scorecard.html')

    def test_compliance_rules(self):
        """Test compliance rules view"""
        response = self.client.get(reverse('compliance:rules'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'compliance/rules.html')

    def test_compliance_alerts(self):
        """Test compliance alerts view"""
        response = self.client.get(reverse('compliance:alerts'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'compliance/alerts.html')
