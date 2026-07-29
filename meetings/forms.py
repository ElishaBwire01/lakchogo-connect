from django import forms
from .models import Meeting, Attendance, MeetingMinutes

class MeetingForm(forms.ModelForm):
    class Meta:
        model = Meeting
        fields = ['title', 'description', 'date', 'venue', 'agenda', 'status']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'date': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'venue': forms.TextInput(attrs={'class': 'form-control'}),
            'agenda': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'status': forms.Select(attrs={'class': 'form-control'}),
        }

class AttendanceForm(forms.ModelForm):
    class Meta:
        model = Attendance
        fields = ['status', 'notes']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }

class MeetingMinutesForm(forms.ModelForm):
    class Meta:
        model = MeetingMinutes
        fields = ['content', 'summary', 'decisions', 'action_items', 'file_attachment']
        widgets = {
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 10}),
            'summary': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'decisions': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'action_items': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'file_attachment': forms.FileInput(attrs={'class': 'form-control'}),
        }
