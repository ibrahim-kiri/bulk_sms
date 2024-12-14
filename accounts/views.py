import logging
import uuid
from django.contrib import messages
from django.contrib.auth import (
    login,
    authenticate,
    update_session_auth_hash,
    logout
)
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse
from . forms import (
    CustomUserCreationForm,
    CustomUserChangeForm,
    ProfileUpdateForm,
    CustomPasswordChangeForm,
    TwoFactorAuthForm
)
from .models import User, Profile, TwoFactorAuth

# Create your views here.
logger = logging.getLogger(__name__)

def register_user(request):
    """
    User registration view
    """
    if request.method == 'POST':
        form =  CustomUserCreationForm(request.POST)
        if form.is_valid():
            try:
                user = form.save(commit=False)
                user.is_active = False  # Require email verification
                user.save()

                # Generate email verification token
                verification_token = str(uuid.uuid4())

                # Send verification email
                verification_link = request.build_absolute_uri(
                    reverse('accounts:verify_email', args=[verification_token])
                )

                send_mail(
                    'Verify Your Email',
                    f'Click the link to verify your email: {verification_link}',
                    settings.DEFAULT_FROM_EMAIL,
                    [user.email],
                    fail_silently=False,
                )

                messages.success(request, 'Registration successful, Please check your email to verify your account.')
                return redirect('accounts:home')  
            
            except Exception as e:
                logger.error(f"Registration error: {str(e)}")
                messages.error(request, "An error occurred during registration.")

    else:
        form = CustomUserCreationForm()

    return render(request, 'accounts/register.html', {'form': form})

def login_user(request):
    """
    User login view
    """
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        user = authenticate(request, email=email, password=password)

        if user is not None:
            if not user.email_verified:
                messages.warning(request, "Please verify your email before logging in.")
                return redirect('accounts:home')
            
            login(request, user)
            messages.success(request, f"Welcome back, {user.get_full_name() or user.username}!")
            return redirect('dashboard')
        else:
            messages.error(request, "Invalid email or password.")

    return render(request, 'accounts/home.html')

@login_required
def profile_update(request):
    """
    Update user profile
    """
    if request.method  == 'POST':
        user_form = CustomUserChangeForm(request.POST, instance=request.user)
        profile_form = ProfileUpdateForm(
            request.POST,
            request.FILES,
            instance=request.user.profile
        )

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, "Profile updated successfully.")
            return redirect('accounts:profile')
    else:
        user_form = CustomUserChangeForm(instance=request.user)
        profile_form = ProfileUpdateForm(instance=request.user.profile)

    return render(request, 'accounts/profile.html', {
        'user_form': user_form,
        'profile_form': profile_form
    })

@login_required
def change_password(request):
    """
    Change user password
    """
    if request.method == 'POST':
        form = CustomPasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, "Password changed successfully.")
            return redirect('accounts:profile')
        else:
            form = CustomPasswordChangeForm(request.user)

        return render(request, 'accounts/change_password.html', {'form': form})
    
def logout_user(request):
    """
    User logout view
    """
    logout(request)
    messages.success(request, "You have been logged out successfully.")
    return redirect('accounts:login')

def verify_email(request, token):
    """
    Email verification view
    """
    try:
        user = User.objects.get(email_verified=False)
        user.email_verified = True
        user.is_active = True
        user.save()

        messages.success(request, "Email verified successfully. You can now log in.")
        return redirect('accounts:login')
    
    except User.DoesNotExist:
        messages.error(request, "Invalid or expired verification token.")
        return redirect('accounts:login')
    
@login_required
def two_factor_settings(request):
    """
    Manage two-factor authentication settings
    """
    try:
        two_factor = request.user.twofactorauth
    except TwoFactorAuth.DoesNotExist:
        two_factor = TwoFactorAuth.objects.create(user_id=request.user)

    if request.method == 'POST':
        form = TwoFactorAuthForm(request.POST, instance=two_factor)
        if form.is_valid():
            form.save()
            messages.success(request, "Two-factor authentication settings updated.")
            return redirect('accounts:profile')
    else:
        form = TwoFactorAuthForm(instance=two_factor)

    return render(request, 'accounts/two_factor_settings.html', {'form': form})
