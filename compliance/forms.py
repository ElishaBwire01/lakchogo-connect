from django import forms
from .models import ComplianceRule, ComplianceScore, ComplianceAlert

class ComplianceRuleForm(forms.ModelForm):
    class Meta:
        model = ComplianceRule
        fields = [
            'name', 'description', 'rule_type', 'target_category',
            'min_attendance_percentage', 'grace_period_days',
            'penalty_points', 'is_active', 'order'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'rule_type': forms.Select(attrs={'class': 'form-control'}),
            'target_category': forms.Select(attrs={'class': 'form-control'}),
            'min_attendance_percentage': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'grace_period_days': forms.NumberInput(attrs={'class': 'form-control'}),
            'penalty_points': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'order': forms.NumberInput(attrs={'class': 'form-control'}),
        }

class ComplianceScoreForm(forms.ModelForm):
    class Meta:
        model = ComplianceScore
        fields = ['score', 'payment_compliance', 'attendance_compliance', 'warnings']
        widgets = {
            'score': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'payment_compliance': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'attendance_compliance': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'warnings': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class ComplianceAlertForm(forms.ModelForm):
    class Meta:
        model = ComplianceAlert
        fields = ['alert_type', 'priority', 'message']
        widgets = {
            'alert_type': forms.Select(attrs={'class': 'form-control'}),
            'priority': forms.Select(attrs={'class': 'form-control'}),
            'message': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
