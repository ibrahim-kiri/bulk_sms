from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Profile, TwoFactorAuth

# Register your models here.
class ProfileInline(admin.StackedInline):
    """
    Inline configuration for profile model in User admin
    """
    model = Profile
    can_delete = False
    verbose_name_plural = 'Profile'
    fk_name = 'users_user_id'

class TwoFactorAuthInline(admin.StackedInline):
    """
    Inline configuration for TwoFactorAuth model in User admin
    """
    model = TwoFactorAuth
    can_delete = False
    verbose_name_plural = 'Two-Factor Authentication'
    fk_name = 'user_id'

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    """
    Custom User Admin configuration
    """
    model = User
    list_display = (
        'email',
        'username',
        'full_name',
        'is_staff',
        'email_verified',
        'credits' if hasattr(User, 'credits') else None
    )
    list_filter = (
        'is_staff',
        'is_superuser',
        'is_active',
        'email_verified'
    )
    fieldsets = (
        (None, {'fields': ('email', 'username', 'password')}),
        ('Personal Info', {'fields': (
            'full_name',
            'phone',
            'address',
            'credits' if hasattr(User, 'credits') else None
        )}),
        ('Permissions', {'fields': (
            'is_active',
            'is_staff',
            'is_superuser',
            'email_verified'
        )}),
        ('Dates', {'fields': ('last_login', 'created_at')}),
    )
    add_fieldsets = (
        (None, {
            'Classes': ('wide',),
            'fields': (
                'email',
                'username',
                'password',
                'full_name'
            ),
        }),
    )
    search_fields = ('email', 'username', 'full_name')
    ordering = ('-created_at',)
    inlines = [ProfileInline, TwoFactorAuthInline]

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    """
    Profile Admin configuration
    """
    list_display = ('__str__', 'profile_picture')
    search_fields = ('users_user_id__username', 'users_user_id__email')

@admin.register(TwoFactorAuth)
class TwoFactorAuthAdmin(admin.ModelAdmin):
    """
    Two-Factor Authentication Admin configuration
    """
    list_display = ('user_id', 'is_enabled', 'last_verified')
    list_filter = ('is_enabled',)
    search_fields = ('user_id__email', 'user_id__username')
