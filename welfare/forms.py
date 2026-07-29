from django import forms
from .models import BereavementEvent, BereavementContribution, WelfareFund, WelfareRequest

class BereavementEventForm(forms.ModelForm):
    class Meta:
        model = BereavementEvent
        fields = ['member', 'deceased_name', 'relationship', 'date_of_death', 'date_of_burial', 'collection_target', 'description']
        widgets = {
            'member': forms.Select(attrs={'class': 'form-control'}),
            'deceased_name': forms.TextInput(attrs={'class': 'form-control'}),
            'relationship': forms.TextInput(attrs={'class': 'form-control'}),
            'date_of_death': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'date_of_burial': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'collection_target': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class BereavementContributionForm(forms.ModelForm):
    class Meta:
        model = BereavementContribution
        fields = ['contributor', 'amount', 'contribution_type', 'payment_method', 'is_public_contribution', 'contributor_name', 'contributor_phone', 'notes']
        widgets = {
            'contributor': forms.Select(attrs={'class': 'form-control'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'contribution_type': forms.Select(attrs={'class': 'form-control'}),
            'payment_method': forms.Select(attrs={'class': 'form-control'}),
            'is_public_contribution': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'contributor_name': forms.TextInput(attrs={'class': 'form-control'}),
            'contributor_phone': forms.TextInput(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }

class WelfareRequestForm(forms.ModelForm):
    class Meta:
        model = WelfareRequest
        fields = ['request_type', 'title', 'description', 'amount_requested', 'supporting_documents']
        widgets = {
            'request_type': forms.Select(attrs={'class': 'form-control'}),
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'amount_requested': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'supporting_documents': forms.FileInput(attrs={'class': 'form-control'}),
        }
