from rest_framework import serializers
from meetings.models import Meeting, Attendance
from api.v1.members.serializers import MemberSerializer

class MeetingSerializer(serializers.ModelSerializer):
    """Serializer for Meeting model"""
    created_by_name = serializers.SerializerMethodField()
    attendance_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Meeting
        fields = [
            'id', 'title', 'description', 'date', 'venue',
            'agenda', 'minutes_text', 'minutes_url', 'status',
            'created_by', 'created_by_name', 'qr_code',
            'attendance_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_created_by_name(self, obj):
        return obj.created_by.get_full_name() if obj.created_by else None
    
    def get_attendance_count(self, obj):
        return obj.attendances.filter(status='present').count()


class AttendanceSerializer(serializers.ModelSerializer):
    """Serializer for Attendance model"""
    member_details = MemberSerializer(source='member', read_only=True)
    recorded_by_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Attendance
        fields = [
            'id', 'meeting', 'member', 'member_details',
            'status', 'check_in_method', 'check_in_time',
            'check_out_time', 'gps_coordinates', 'notes',
            'recorded_by', 'recorded_by_name', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_recorded_by_name(self, obj):
        return obj.recorded_by.get_full_name() if obj.recorded_by else None
