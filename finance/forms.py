from django import forms
from .models import PaymentCategory, Payment, PaymentReceipt, PaymentReminder

class PaymentCategoryForm(forms.ModelForm):
    class Meta:
        model = PaymentCategory
        fields = ['name', 'description', 'default_amount', 'frequency', 'is_mandatory_for_welfare', 'color', 'icon', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'default_amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'frequency': forms.Select(attrs={'class': 'form-control'}),
            'is_mandatory_for_welfare': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'color': forms.Select(attrs={'class': 'form-control'}),
            'icon': forms.TextInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ['member', 'category', 'amount', 'payment_method', 'transaction_ref', 'notes']
        widgets = {
            'member': forms.Select(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'payment_method': forms.Select(attrs={'class': 'form-control'}),
            'transaction_ref': forms.TextInput(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }

class PaymentReceiptForm(forms.ModelForm):
    class Meta:
        model = PaymentReceipt
        fields = ['payment', 'receipt_number', 'pdf_file', 'html_content']
        widgets = {
            'payment': forms.Select(attrs={'class': 'form-control'}),
            'receipt_number': forms.TextInput(attrs={'class': 'form-control'}),
            'pdf_file': forms.FileInput(attrs={'class': 'form-control'}),
            'html_content': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
        }

class PaymentReminderForm(forms.ModelForm):
    class Meta:
        model = PaymentReminder
        fields = ['member', 'category', 'reminder_type', 'message']
        widgets = {
            'member': forms.Select(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'reminder_type': forms.Select(attrs={'class': 'form-control'}),
            'message': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
