from django.utils import timezone
from django.conf import settings
from .models import Notification

class NotificationService:
    """Service for creating and managing notifications"""
    
    @staticmethod
    def send_notification(user, notification_type, title, message, 
                         channel='in_app', action_url=None, priority='normal',
                         related_id=None, related_model=None):
        """Create a notification for a user"""
        return Notification.create_notification(
            recipient=user,
            notification_type=notification_type,
            title=title,
            message=message,
            channel=channel,
            action_url=action_url,
            priority=priority,
            related_id=related_id,
            related_model=related_model
        )
    
    @staticmethod
    def send_bulk_notification(users, notification_type, title, message,
                               channel='in_app', action_url=None, priority='normal',
                               related_id=None, related_model=None):
        """Create notifications for multiple users"""
        return Notification.create_bulk_notifications(
            recipients=users,
            notification_type=notification_type,
            title=title,
            message=message,
            channel=channel,
            action_url=action_url,
            priority=priority,
            related_id=related_id,
            related_model=related_model
        )
    
    @staticmethod
    def get_unread_count(user):
        """Get unread notification count for a user"""
        return Notification.objects.filter(
            recipient=user,
            status__in=['pending', 'sent', 'delivered']
        ).count()
    
    @staticmethod
    def get_all_notifications(user, limit=20):
        """Get notifications for a user"""
        return Notification.objects.filter(
            recipient=user
        ).order_by('-created_at')[:limit]
    
    @staticmethod
    def mark_all_read(user):
        """Mark all notifications as read for a user"""
        updated = Notification.objects.filter(
            recipient=user,
            status__in=['pending', 'sent', 'delivered']
        ).update(status='read', read_at=timezone.now())
        return updated


# ============================================
# Notification Triggers
# ============================================

class NotificationTriggers:
    """Trigger notifications for various events"""
    
    @staticmethod
    def payment_created(payment):
        """Notify when a payment is created"""
        # Notify member
        NotificationService.send_notification(
            user=payment.member.user,
            notification_type='payment_received',
            title='💰 Payment Received',
            message=f'Your payment of KES {payment.amount} for {payment.category.name} has been recorded.',
            action_url=f'/finance/payments/{payment.id}/',
            related_id=payment.id,
            related_model='Payment'
        )
        
        # Notify treasurer (if different from member)
        if payment.recorded_by and payment.recorded_by != payment.member.user:
            NotificationService.send_notification(
                user=payment.recorded_by,
                notification_type='payment_received',
                title='💰 Payment Recorded',
                message=f'Payment of KES {payment.amount} recorded for {payment.member.get_full_name()}',
                action_url=f'/finance/payments/{payment.id}/',
                related_id=payment.id,
                related_model='Payment'
            )
    
    @staticmethod
    def payment_approved(payment):
        """Notify when a payment is approved"""
        NotificationService.send_notification(
            user=payment.member.user,
            notification_type='payment_approved',
            title='✅ Payment Approved',
            message=f'Your payment of KES {payment.amount} for {payment.category.name} has been approved.',
            action_url=f'/finance/payments/{payment.id}/',
            related_id=payment.id,
            related_model='Payment'
        )
    
    @staticmethod
    def member_registered(member):
        """Notify when a new member registers"""
        # Send welcome notification to the new member
        NotificationService.send_notification(
            user=member.user,
            notification_type='member_registered',
            title='🎉 Welcome to LakChogo Connect!',
            message=f'Welcome {member.get_full_name()}! Your member ID is {member.member_id}. We are glad to have you!',
            action_url='/dashboard/',
            related_id=member.id,
            related_model='Member',
            priority='high'
        )
        
        # Also send a welcome email (simplified - create notification)
        NotificationService.send_notification(
            user=member.user,
            notification_type='system',
            title='📋 Getting Started',
            message='Complete your profile, make your first payment, and attend upcoming meetings.',
            action_url='/accounts/profile/',
            related_id=member.id,
            related_model='Member'
        )
        
        # Notify committee members
        from accounts.models import UserRole
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        committee_users = UserRole.objects.filter(
            role__name__in=['Admin', 'Secretary'],
            is_active=True
        ).values_list('user', flat=True)
        
        committee_members = User.objects.filter(id__in=committee_users, is_active=True)
        
        if committee_members.exists():
            NotificationService.send_bulk_notification(
                users=committee_members,
                notification_type='member_registered',
                title='👤 New Member Registered',
                message=f'{member.get_full_name()} has joined the group. Member ID: {member.member_id}',
                action_url=f'/members/{member.member_id}/',
                related_id=member.id,
                related_model='Member'
            )
    
    @staticmethod
    def meeting_scheduled(meeting):
        """Notify when a meeting is scheduled"""
        from members.models import Member
        
        # Get all active members
        members = Member.objects.filter(status='active')
        users = [m.user for m in members if m.user and m.user.is_active]
        
        # Format date nicely
        try:
            date_str = meeting.date.strftime("%B %d, %Y at %H:%M")
        except:
            date_str = str(meeting.date)
        
        # Send to all members
        if users:
            NotificationService.send_bulk_notification(
                users=users,
                notification_type='meeting_scheduled',
                title=f'📅 New Meeting: {meeting.title}',
                message=f'Meeting: {meeting.title} on {date_str} at {meeting.venue}',
                action_url=f'/meetings/{meeting.id}/',
                related_id=meeting.id,
                related_model='Meeting'
            )
        
        # Also notify committee separately
        from accounts.models import UserRole
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        committee_users = UserRole.objects.filter(
            role__name__in=['Admin', 'Secretary', 'Treasurer', 'Welfare Officer'],
            is_active=True
        ).values_list('user', flat=True)
        
        committee_members = User.objects.filter(id__in=committee_users, is_active=True)
        
        if committee_members.exists():
            NotificationService.send_bulk_notification(
                users=committee_members,
                notification_type='meeting_scheduled',
                title=f'📅 Committee: {meeting.title}',
                message=f'Committee meeting scheduled: {meeting.title} on {date_str} at {meeting.venue}',
                action_url=f'/meetings/{meeting.id}/',
                related_id=meeting.id,
                related_model='Meeting',
                priority='high'
            )
    
    @staticmethod
    def meeting_reminder(meeting):
        """Send meeting reminder"""
        from members.models import Member
        
        members = Member.objects.filter(status='active')
        users = [m.user for m in members if m.user and m.user.is_active]
        
        try:
            date_str = meeting.date.strftime("%B %d, %Y at %H:%M")
        except:
            date_str = str(meeting.date)
        
        if users:
            NotificationService.send_bulk_notification(
                users=users,
                notification_type='meeting_reminder',
                title=f'⏰ Reminder: {meeting.title}',
                message=f'Reminder: {meeting.title} tomorrow at {date_str} at {meeting.venue}',
                action_url=f'/meetings/{meeting.id}/',
                related_id=meeting.id,
                related_model='Meeting',
                priority='high'
            )
    
    @staticmethod
    def meeting_cancelled(meeting):
        """Notify when a meeting is cancelled"""
        from members.models import Member
        
        members = Member.objects.filter(status='active')
        users = [m.user for m in members if m.user and m.user.is_active]
        
        if users:
            NotificationService.send_bulk_notification(
                users=users,
                notification_type='meeting_cancelled',
                title=f'❌ Meeting Cancelled: {meeting.title}',
                message=f'The meeting "{meeting.title}" scheduled for {meeting.date} has been cancelled.',
                action_url='/meetings/',
                related_id=meeting.id,
                related_model='Meeting',
                priority='high'
            )
    
    @staticmethod
    def attendance_recorded(attendance):
        """Notify when attendance is recorded"""
        if attendance.status == 'present':
            NotificationService.send_notification(
                user=attendance.member.user,
                notification_type='attendance_alert',
                title='✅ Attendance Recorded',
                message=f'Your attendance for {attendance.meeting.title} has been recorded.',
                action_url=f'/meetings/{attendance.meeting.id}/',
                related_id=attendance.meeting.id,
                related_model='Meeting'
            )
    
    @staticmethod
    def welfare_event_created(event):
        """Notify when a welfare event is created"""
        from members.models import Member
        
        members = Member.objects.filter(status='active')
        users = [m.user for m in members if m.user and m.user.is_active]
        
        if users:
            NotificationService.send_bulk_notification(
                users=users,
                notification_type='welfare_event',
                title=f'🕊️ Bereavement: {event.deceased_name}',
                message=f'Bereavement event for {event.deceased_name}. Target: KES {event.collection_target}',
                action_url=f'/welfare/{event.id}/',
                related_id=event.id,
                related_model='BereavementEvent',
                priority='high'
            )
    
    @staticmethod
    def welfare_target_reached(event):
        """Notify when welfare target is reached"""
        from members.models import Member
        
        members = Member.objects.filter(status='active')
        users = [m.user for m in members if m.user and m.user.is_active]
        
        if users:
            NotificationService.send_bulk_notification(
                users=users,
                notification_type='welfare_target',
                title=f'🎯 Target Reached! {event.deceased_name}',
                message=f'Collection target for {event.deceased_name} has been reached. KES {event.amount_collected} collected.',
                action_url=f'/welfare/{event.id}/',
                related_id=event.id,
                related_model='BereavementEvent',
                priority='high'
            )
    
    @staticmethod
    def welfare_contribution_made(contribution):
        """Notify when a welfare contribution is made"""
        # Notify the contributor
        if contribution.contributor:
            NotificationService.send_notification(
                user=contribution.contributor.user,
                notification_type='welfare_alert',
                title='❤️ Contribution Received',
                message=f'Your contribution of KES {contribution.amount} for {contribution.event.deceased_name} has been recorded.',
                action_url=f'/welfare/{contribution.event.id}/',
                related_id=contribution.event.id,
                related_model='BereavementEvent'
            )
        
        # Notify welfare officer
        from accounts.models import UserRole
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        welfare_roles = UserRole.objects.filter(
            role__name__in=['Welfare Officer', 'Admin'],
            is_active=True
        ).values_list('user', flat=True)
        
        welfare_users = User.objects.filter(id__in=welfare_roles, is_active=True)
        
        if welfare_users.exists():
            NotificationService.send_bulk_notification(
                users=welfare_users,
                notification_type='welfare_alert',
                title='💰 Contribution Received',
                message=f'{contribution.contributor_name} contributed KES {contribution.amount} for {contribution.event.deceased_name}',
                action_url=f'/welfare/{contribution.event.id}/',
                related_id=contribution.event.id,
                related_model='BereavementEvent'
            )
    
    @staticmethod
    def compliance_updated(compliance_score):
        """Notify when compliance is updated"""
        # Only notify if status changed or is critical
        if compliance_score.status == 'red':
            NotificationService.send_notification(
                user=compliance_score.member.user,
                notification_type='compliance_alert',
                title='⚠️ Compliance Alert - Action Required',
                message=f'Your compliance score is {compliance_score.score}%. Please take action immediately.',
                action_url=f'/compliance/member/{compliance_score.member.member_id}/',
                related_id=compliance_score.id,
                related_model='ComplianceScore',
                priority='urgent'
            )
        elif compliance_score.status == 'yellow':
            NotificationService.send_notification(
                user=compliance_score.member.user,
                notification_type='compliance_update',
                title='📊 Compliance Update',
                message=f'Your compliance score is {compliance_score.score}%. Check your status.',
                action_url=f'/compliance/member/{compliance_score.member.member_id}/',
                related_id=compliance_score.id,
                related_model='ComplianceScore'
            )
        elif compliance_score.status == 'green' and compliance_score.score >= 80:
            NotificationService.send_notification(
                user=compliance_score.member.user,
                notification_type='compliance_update',
                title='✅ Good Standing',
                message=f'Your compliance score is {compliance_score.score}%. You are in good standing!',
                action_url=f'/compliance/member/{compliance_score.member.member_id}/',
                related_id=compliance_score.id,
                related_model='ComplianceScore'
            )
    
    @staticmethod
    def report_generated(report):
        """Notify when a report is generated"""
        NotificationService.send_notification(
            user=report.generated_by,
            notification_type='report_ready',
            title='📊 Report Ready',
            message=f'Your {report.get_report_type_display()} report is ready for download.',
            action_url=f'/reports/{report.id}/',
            related_id=report.id,
            related_model='Report'
        )
    
    @staticmethod
    def announcement_published(announcement):
        """Notify when an announcement is published"""
        from django.contrib.auth import get_user_model
        User = get_user_model()
        users = User.objects.filter(is_active=True)
        
        if users.exists():
            NotificationService.send_bulk_notification(
                users=users,
                notification_type='announcement',
                title=f'📢 {announcement.title}',
                message=announcement.content[:200],
                action_url=f'/communications/announcements/{announcement.id}/',
                related_id=announcement.id,
                related_model='Announcement',
                priority='normal'
            )

    @staticmethod
    def chat_message_notification(message, recipient):
        """Send notification for a chat message"""
        NotificationService.send_notification(
            user=recipient,
            notification_type='chat_message',
            title=f'💬 New message from {message.sender.get_full_name()}',
            message=message.content[:100],
            action_url=f'/communications/chat/{message.room.id}/',
            related_id=message.room.id,
            related_model='ChatRoom'
        )

    @staticmethod
    def chat_message_notification(message, recipient):
        """Send a chat message notification that auto-dismisses"""
        # Create notification in database
        NotificationService.send_notification(
            user=recipient,
            notification_type='chat_message',
            title=f'💬 New message from {message.sender.get_full_name()}',
            message=message.content[:100],
            action_url=f'/communications/chat/{message.room.id}/',
            related_id=message.room.id,
            related_model='ChatRoom'
        )
        
        # The frontend will show a toast notification that auto-dismisses after 1 second
        # This is handled in the chat room template
