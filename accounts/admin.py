from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Profile

# Register your models here.
class ProfileInline(admin.StackedInline):
    """
    Inline configuration for profile model in User admin
    """
    model = Profile
    can_delete = False
    verbose_name_plural = 'Profile'
    fk_name = 'users_user_id'

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    """
    Custom User Admin configuration
    """
    model = User
    list_display = (
        'username',
        'email',
        'full_name',
        'is_staff',
        *(['credits'] if hasattr(User, 'credits') else [])
    )
    list_filter = (
        'is_staff',
        'is_superuser',
        'is_active',
    )
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal Info', {'fields': (
            'full_name',
            'email'
            'phone',
            'address',
            'credits' if hasattr(User, 'credits') else None
        )}),
        ('Permissions', {'fields': (
            'is_active',
            'is_staff',
            'is_superuser',
        )}),
        ('Dates', {'fields': ('last_login', 'created_at')}),
    )
    add_fieldsets = (
        (None, {
            'Classes': ('wide',),
            'fields': (
                'username',
                'email',
                'password',
                'full_name'
            ),
        }),
    )
    search_fields = ('username', 'email', 'full_name')
    ordering = ('-created_at',)
    inlines = [ProfileInline]

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    """
    Profile Admin configuration
    """
    list_display = ('__str__', 'profile_picture')
    search_fields = ('users_user_id__username', 'users_user_id__email')
