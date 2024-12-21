import logging
from django.contrib import messages
from django.contrib.auth import (
    login,
    authenticate,
    update_session_auth_hash,
    logout
)
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from . forms import (
    CustomUserCreationForm,
    CustomUserChangeForm,
    ProfileUpdateForm,
    CustomPasswordChangeForm,
)

# Create your views here.
logger = logging.getLogger(__name__)

def home_view(request):
    """
    Home page view that displays the login form
    """
    if request.user.is_authenticated:
        return redirect('accounts:dashboard')
    return render(request, 'home.html')

def register_user(request):
    """
    User registration view
    """
    if request.method == 'POST':
        form =  CustomUserCreationForm(request.POST)
        if form.is_valid():
            try:
                user = form.save(commit=False)
                # user.is_active = False
                user.save()
                messages.success(request, 'Registration successful!')
                return redirect('home')  
            except Exception as e:
                logger.error(f"Registration error: {str(e)}")
                messages.error(request, "An error occurred during registration.")
                return render(request, 'accounts/register.html', {'form': form})
        else:
            # Form is not valid, render the template with form errors
            messages.error(request, "Please correct the errors below.")
    else:
        form = CustomUserCreationForm()

    return render(request, 'accounts/register.html', {'form': form})

def login_user(request):
    """
    User login view
    """
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            if user.is_active:
                login(request, user)
                messages.success(request, f"Welcome back, {user.get_full_name() or user.username}!")
                return redirect('accounts:dashboard')
            else:
                messages.error(request, "Your account is not active.")
        else:
            messages.error(request, "Invalid username or password.")

    return render(request, 'home.html')

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
    
@login_required(login_url='accounts:home')
def dashboard(request):
    """
    Dashboard view for authenticated users
    """
    return render(request, 'dashboard.html')

def logout_user(request):
    """
    User logout view
    """

    # Clear any success messages before logout
    storage = messages.get_messages(request)
    storage.used = True

    logout(request)
    messages.success(request, "You have been logged out successfully.")
    return redirect('home')