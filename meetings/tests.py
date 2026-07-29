from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from .models import Meeting, Attendance
from members.models import Member

User = get_user_model()

class MeetingModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            phone='+254712345678',
            password='TestPassword123'
        )
        self.meeting = Meeting.objects.create(
            title='Test Meeting',
            date=timezone.now() + timezone.timedelta(days=1),
            venue='Test Venue',
            created_by=self.user,
            status='scheduled'
        )
    
    def test_meeting_creation(self):
        self.assertEqual(self.meeting.title, 'Test Meeting')
        self.assertEqual(self.meeting.venue, 'Test Venue')
        self.assertEqual(self.meeting.status, 'scheduled')
    
    def test_meeting_is_upcoming(self):
        self.assertTrue(self.meeting.is_upcoming())
    
    def test_meeting_str(self):
        self.assertIn('Test Meeting', str(self.meeting))

class AttendanceModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            phone='+254712345678',
            password='TestPassword123'
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
        self.assertEqual(self.attendance.status, 'present')
        self.assertEqual(str(self.attendance), 'testuser - Test Meeting - present')
    
    def test_mark_present(self):
        self.attendance.mark_absent()
        self.assertEqual(self.attendance.status, 'absent')
    
    def test_mark_excused(self):
        self.attendance.mark_excused()
        self.assertEqual(self.attendance.status, 'excused')
