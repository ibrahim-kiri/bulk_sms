from django import forms
from django.contrib.auth.forms import (
    UserCreationForm,
    UserChangeForm,
    PasswordChangeForm
)
from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _
from .models import User, Profile

class CustomUserCreationForm(UserCreationForm):
    """
    Form for creating a new user
    """
    phone = forms.CharField(
        max_length=10,
        validators=[
            RegexValidator(
                regex=r'^07\d{8}$',
                message='Phone number must be in format: 0771200001',
                code='invalid_phone'
            )
        ]
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'email', 'full_name', 'phone', 'address')
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'full_name': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.TextInput(attrs={'class': 'form-control'})
        }
    
class CustomUserChangeForm(UserChangeForm):
    """
    Form for updating user information
    """
    class Meta:
        model = User
        fields = ('username', 'full_name', 'email', 'phone', 'address')
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'full_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.TextInput(attrs={'class': 'form-control', 'required': False}),
            'phone': forms.Textarea(attrs={'class': 'form-control'}),
            'address': forms.EmailInput(attrs={'class': 'form-control', 'rows': 3}),
        }

class ProfileUpdateForm(forms.ModelForm):
    """
    Form for updating user profile
    """
    class Meta:
        model = Profile
        fields = ('profile_picture',)
        widgets = {
            'profile_picture': forms.FileInput(attrs={'class': 'form-control-file'}),
        }

class CustomPasswordChangeForm(PasswordChangeForm):
    """
    Custom password change form with bootstrap classes
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add bootstrap classes to form fields
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})