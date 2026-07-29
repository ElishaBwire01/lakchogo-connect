"""
Members Tests for LakChogo Connect
"""

from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from members.models import Member, MemberNote, MemberContributionSummary

User = get_user_model()

class MemberModelTest(TestCase):
    """Test Member model"""

    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username='testuser',
            phone='+254712345678',
            password='TestPass123',
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
        """Test member creation"""
        self.assertEqual(self.member.get_full_name(), 'Test User')
        self.assertEqual(self.member.status, 'active')
        self.assertTrue(self.member.is_active)
        self.assertIsNotNone(self.member.member_id)
        self.assertTrue(self.member.member_id.startswith('LCG-'))

    def test_member_str(self):
        """Test member string representation"""
        self.assertIn('LCG-', str(self.member))
        self.assertIn('Test User', str(self.member))

    def test_member_activation(self):
        """Test member activation"""
        self.member.status = 'pending'
        self.member.save()
        self.member.activate()
        self.assertEqual(self.member.status, 'active')

    def test_member_suspension(self):
        """Test member suspension"""
        self.member.suspend()
        self.assertEqual(self.member.status, 'suspended')

    def test_member_deactivation(self):
        """Test member deactivation"""
        self.member.deactivate()
        self.assertEqual(self.member.status, 'inactive')

    def test_member_properties(self):
        """Test member properties"""
        self.assertTrue(self.member.is_active)
        self.assertEqual(self.member.compliance_status, 'green')

    def test_member_id_generation(self):
        """Test member ID auto-generation"""
        member2 = Member.objects.create(user=self.user, status='active')
        self.assertNotEqual(self.member.member_id, member2.member_id)

class MemberNoteTest(TestCase):
    """Test MemberNote model"""

    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username='testuser',
            phone='+254712345678',
            password='TestPass123'
        )
        self.member = Member.objects.create(user=self.user)
        self.note = MemberNote.objects.create(
            member=self.member,
            author=self.user,
            content='Test note content',
            is_private=False
        )

    def test_note_creation(self):
        """Test note creation"""
        self.assertEqual(self.note.content, 'Test note content')
        self.assertEqual(self.note.member, self.member)
        self.assertEqual(self.note.author, self.user)
        self.assertFalse(self.note.is_private)

    def test_note_str(self):
        """Test note string representation"""
        self.assertIn('Test User', str(self.note))

class MemberContributionSummaryTest(TestCase):
    """Test MemberContributionSummary model"""

    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username='testuser',
            phone='+254712345678',
            password='TestPass123'
        )
        self.member = Member.objects.create(user=self.user)
        self.summary = MemberContributionSummary.objects.create(
            member=self.member,
            total_paid=500,
            total_expected=1000,
            balance=500
        )

    def test_summary_creation(self):
        """Test contribution summary creation"""
        self.assertEqual(self.summary.total_paid, 500)
        self.assertEqual(self.summary.total_expected, 1000)
        self.assertEqual(self.summary.balance, 500)

    def test_summary_str(self):
        """Test summary string representation"""
        self.assertIn('Test User', str(self.summary))
        self.assertIn('500', str(self.summary))

class MemberViewsTest(TestCase):
    """Test Member views"""

    def setUp(self):
        """Set up test data"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            phone='+254712345678',
            password='TestPass123',
            first_name='Test',
            last_name='User'
        )
        self.member = Member.objects.create(user=self.user, status='active')
        self.client.login(username='testuser', password='TestPass123')

    def test_member_list_view(self):
        """Test member list view"""
        response = self.client.get(reverse('members:list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'members/list.html')

    def test_member_detail_view(self):
        """Test member detail view"""
        response = self.client.get(reverse('members:detail', args=[self.member.member_id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'members/detail.html')

    def test_member_register_view(self):
        """Test member register view"""
        response = self.client.get(reverse('members:register'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'members/register.html')

    def test_member_search_view(self):
        """Test member search view"""
        response = self.client.get(reverse('members:search'), {'q': 'Test'})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'members/search.html')

    def test_member_status_view(self):
        """Test member status view"""
        response = self.client.get(reverse('members:status', args=[self.member.member_id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'members/status.html')

    def test_member_edit_view(self):
        """Test member edit view"""
        response = self.client.get(reverse('members:edit', args=[self.member.member_id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'members/edit.html')
