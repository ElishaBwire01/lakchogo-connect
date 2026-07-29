from django.test import TestCase
from django.contrib.auth import get_user_model
from .models import Member, MemberNote, MemberContributionSummary

User = get_user_model()

class MemberModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            phone='+254712345678',
            password='TestPassword123',
            first_name='Test',
            last_name='User',
            id_number='12345678'
        )
        self.member = Member.objects.create(
            user=self.user,
            status='active',
            next_of_kin_name='Jane Doe',
            next_of_kin_phone='+254798765432',
            next_of_kin_relationship='Sister'
        )
    
    def test_member_creation(self):
        self.assertEqual(self.member.get_full_name(), 'Test User')
        self.assertEqual(self.member.status, 'active')
        self.assertTrue(self.member.is_active)
        self.assertIsNotNone(self.member.member_id)
        self.assertTrue(self.member.member_id.startswith('LCG-'))
    
    def test_member_str(self):
        self.assertIn('LCG-', str(self.member))
        self.assertIn('Test User', str(self.member))
    
    def test_activate_member(self):
        self.member.status = 'pending'
        self.member.save()
        self.member.activate()
        self.assertEqual(self.member.status, 'active')
    
    def test_suspend_member(self):
        self.member.suspend()
        self.assertEqual(self.member.status, 'suspended')
    
    def test_deactivate_member(self):
        self.member.deactivate()
        self.assertEqual(self.member.status, 'inactive')
    
    def test_member_properties(self):
        self.assertTrue(self.member.is_active)
        self.assertEqual(self.member.compliance_status, 'green')

class MemberNoteTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            phone='+254712345678',
            password='TestPassword123'
        )
        self.member = Member.objects.create(user=self.user)
        self.note = MemberNote.objects.create(
            member=self.member,
            author=self.user,
            content='Test note content',
            is_private=False
        )
    
    def test_note_creation(self):
        self.assertEqual(self.note.content, 'Test note content')
        self.assertEqual(self.note.member, self.member)
        self.assertEqual(self.note.author, self.user)
        self.assertFalse(self.note.is_private)
    
    def test_note_str(self):
        self.assertIn('Test User', str(self.note))

class MemberContributionSummaryTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            phone='+254712345678',
            password='TestPassword123'
        )
        self.member = Member.objects.create(user=self.user)
        self.summary = MemberContributionSummary.objects.create(
            member=self.member,
            total_paid=500,
            total_expected=1000,
            balance=500
        )
    
    def test_summary_creation(self):
        self.assertEqual(self.summary.total_paid, 500)
        self.assertEqual(self.summary.total_expected, 1000)
        self.assertEqual(self.summary.balance, 500)
    
    def test_summary_str(self):
        self.assertIn('Test User', str(self.summary))
        self.assertIn('500', str(self.summary))
