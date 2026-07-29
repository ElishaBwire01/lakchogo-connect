"""
Meetings Tests for LakChogo Connect
"""

from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from members.models import Member
from meetings.models import Meeting, Attendance, MeetingMinutes

User = get_user_model()

class MeetingModelTest(TestCase):
    """Test Meeting model"""

    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username='testuser',
            phone='+254712345678',
            password='TestPass123'
        )
        self.meeting = Meeting.objects.create(
            title='Test Meeting',
            date=timezone.now() + timezone.timedelta(days=1),
            venue='Test Venue',
            created_by=self.user,
            status='scheduled'
        )

    def test_meeting_creation(self):
        """Test meeting creation"""
        self.assertEqual(self.meeting.title, 'Test Meeting')
        self.assertEqual(self.meeting.venue, 'Test Venue')
        self.assertEqual(self.meeting.status, 'scheduled')

    def test_meeting_is_upcoming(self):
        """Test meeting is upcoming"""
        self.assertTrue(self.meeting.is_upcoming())

    def test_meeting_str(self):
        """Test meeting string representation"""
        self.assertIn('Test Meeting', str(self.meeting))

    def test_meeting_attendance_count(self):
        """Test meeting attendance count"""
        self.assertEqual(self.meeting.get_attendance_count(), 0)

class AttendanceModelTest(TestCase):
    """Test Attendance model"""

    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username='testuser',
            phone='+254712345678',
            password='TestPass123'
        )
        self.member = Member.objects.create(user=self.user)
        self.meeting = Meeting.objects.create(
            title='Test Meeting',
            date=timezone.now(),
            venue='Test Venue',
            created_by=self.user
        )
        self.attendance = Attendance.objects.create(
            meeting=self.meeting,
            member=self.member,
            status='present'
        )

    def test_attendance_creation(self):
        """Test attendance creation"""
        self.assertEqual(self.attendance.status, 'present')
        self.assertEqual(str(self.attendance), f'{self.member.get_full_name()} - Test Meeting - present')

    def test_mark_present(self):
        """Test mark present"""
        self.attendance.mark_absent()
        self.assertEqual(self.attendance.status, 'absent')

    def test_mark_excused(self):
        """Test mark excused"""
        self.attendance.mark_excused()
        self.assertEqual(self.attendance.status, 'excused')

class MeetingViewsTest(TestCase):
    """Test Meeting views"""

    def setUp(self):
        """Set up test data"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            phone='+254712345678',
            password='TestPass123'
        )
        self.member = Member.objects.create(user=self.user, status='active')
        self.meeting = Meeting.objects.create(
            title='Test Meeting',
            date=timezone.now() + timezone.timedelta(days=1),
            venue='Test Venue',
            created_by=self.user,
            status='scheduled'
        )
        self.client.login(username='testuser', password='TestPass123')

    def test_meeting_list(self):
        """Test meeting list view"""
        response = self.client.get(reverse('meetings:index'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'meetings/index.html')

    def test_meeting_detail(self):
        """Test meeting detail view"""
        response = self.client.get(reverse('meetings:detail', args=[self.meeting.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'meetings/detail.html')

    def test_meeting_schedule(self):
        """Test meeting schedule view"""
        response = self.client.get(reverse('meetings:schedule'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'meetings/schedule.html')

    def test_meeting_attendance(self):
        """Test meeting attendance view"""
        response = self.client.get(reverse('meetings:attendance', args=[self.meeting.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'meetings/attendance.html')

    def test_meeting_edit(self):
        """Test meeting edit view"""
        response = self.client.get(reverse('meetings:edit', args=[self.meeting.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'meetings/edit.html')

    def test_upload_minutes(self):
        """Test upload minutes view"""
        response = self.client.get(reverse('meetings:upload_minutes', args=[self.meeting.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'meetings/upload_minutes.html')
