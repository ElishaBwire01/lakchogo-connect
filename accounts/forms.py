from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.core.exceptions import ValidationError
from .models import User, Role

class UserRegistrationForm(UserCreationForm):
    """Form for user registration"""
    phone = forms.CharField(
        max_length=17,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+254712345678'})
    )
    id_number = forms.CharField(
        max_length=20,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'National ID Number'})
    )
    first_name = forms.CharField(
        max_length=30,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'})
    )
    last_name = forms.CharField(
        max_length=30,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'})
    )
    email = forms.EmailField(
        required=False,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email Address'})
    )
    
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'phone', 'id_number', 'email', 'password1', 'password2']
    
    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if User.objects.filter(phone=phone).exists():
            raise ValidationError('Phone number already registered')
        return phone
    
    def clean_id_number(self):
        id_number = self.cleaned_data.get('id_number')
        if User.objects.filter(id_number=id_number).exists():
            raise ValidationError('ID number already registered')
        return id_number


class UserLoginForm(forms.Form):
    """Form for user login"""
    username = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username or Phone'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'})
    )


class UserProfileForm(forms.ModelForm):
    """Form for updating user profile"""
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'phone', 'email', 'profile_picture']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'profile_picture': forms.FileInput(attrs={'class': 'form-control'}),
        }


class RoleForm(forms.ModelForm):
    """Form for creating/editing roles"""
    class Meta:
        model = Role
        fields = ['name', 'description', 'permissions', 'is_default']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'permissions': forms.SelectMultiple(attrs={'class': 'form-control'}),
            'is_default': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
