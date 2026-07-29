from django import forms
from django.contrib.auth import get_user_model
from .models import Member, MemberNote, MemberDocument

User = get_user_model()

class MemberRegistrationForm(forms.ModelForm):
    """Form for registering a new member"""
    username = forms.CharField(max_length=150)
    first_name = forms.CharField(max_length=30)
    last_name = forms.CharField(max_length=30)
    phone = forms.CharField(max_length=17)
    id_number = forms.CharField(max_length=20)
    email = forms.EmailField(required=False)
    password = forms.CharField(widget=forms.PasswordInput)
    password_confirm = forms.CharField(widget=forms.PasswordInput)
    
    class Meta:
        model = Member
        fields = [
            'username', 'first_name', 'last_name', 'phone', 'id_number', 'email',
            'password', 'password_confirm',
            'next_of_kin_name', 'next_of_kin_phone', 'next_of_kin_relationship',
            'date_of_birth', 'gender', 'occupation', 'address',
            'emergency_contact_name', 'emergency_contact_phone', 'emergency_contact_relationship'
        ]
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
            'gender': forms.Select(choices=(('', 'Select Gender'), ('male', 'Male'), ('female', 'Female'), ('other', 'Other'))),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')
        
        if password and password_confirm and password != password_confirm:
            raise forms.ValidationError('Passwords do not match.')
        return cleaned_data
    
    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError('Username already exists.')
        return username
    
    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if User.objects.filter(phone=phone).exists():
            raise forms.ValidationError('Phone number already registered.')
        return phone
    
    def clean_id_number(self):
        id_number = self.cleaned_data.get('id_number')
        if User.objects.filter(id_number=id_number).exists():
            raise forms.ValidationError('ID number already registered.')
        return id_number


class MemberEditForm(forms.ModelForm):
    """Form for editing member details"""
    first_name = forms.CharField(max_length=30)
    last_name = forms.CharField(max_length=30)
    phone = forms.CharField(max_length=17)
    email = forms.EmailField(required=False)
    
    class Meta:
        model = Member
        fields = [
            'first_name', 'last_name', 'phone', 'email',
            'date_of_birth', 'gender', 'occupation', 'address',
            'next_of_kin_name', 'next_of_kin_phone', 'next_of_kin_relationship',
            'next_of_kin_address', 'status', 'member_notes',  # CHANGED: notes to member_notes
            'emergency_contact_name', 'emergency_contact_phone', 'emergency_contact_relationship'
        ]
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
            'gender': forms.Select(choices=(('', 'Select Gender'), ('male', 'Male'), ('female', 'Female'), ('other', 'Other'))),
            'status': forms.Select(choices=(('active', 'Active'), ('inactive', 'Inactive'), ('suspended', 'Suspended'), ('pending', 'Pending'))),
            'member_notes': forms.Textarea(attrs={'rows': 4}),  # CHANGED: notes to member_notes
        }


class MemberNoteForm(forms.ModelForm):
    class Meta:
        model = MemberNote
        fields = ['content', 'is_private']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 4}),
            'is_private': forms.CheckboxInput(),
        }
