from django import forms
from django.contrib.auth.forms import (
    UserCreationForm,
    UserChangeForm,
    PasswordChangeForm
)
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
import re
from .models import User, Profile, TwoFactorAuth

class CustomUserCreationForm(UserCreationForm):
    """
    Form for creating a new user
    """
    email = forms.EmailField(
        label=_("Email"),
        max_length=254,
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )
    phone = forms.CharField(
        label=_("Phone Number"),
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        help_text=_("Enter phone number with country code, e.g., +256701234567")
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'email', 'full_name', 'phone', 'password')
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'full_name': forms.TextInput(attrs={'class': 'form-control'}),
            'password': forms.PasswordInput(attrs={'class': 'form-control'})
        }

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if phone:
            # Validate phone number format
            if not re.match(r'^\+?1?\d{9,15}$', phone):
                raise ValidationError(_("Invalid phone number format."))
        return phone
    
class CustomUserChangeForm(UserChangeForm):
    """
    Form for updating user information
    """
    class Meta:
        model = User
        fields = ('full_name', 'phone', 'address', 'email')
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
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

class TwoFactorAuthForm(forms.ModelForm):
    """
    Form for managing two-factor authentication settings
    """
    class Meta:
        model = TwoFactorAuth
        fields = ('is_enabled',)
        widgets = {
            'is_enabled': forms.CheckboxInput(attrs={'class': 'form-check-input'})
        }