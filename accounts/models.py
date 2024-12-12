from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.core.validators import EmailValidator
from django.db.models.signals import post_save
from django.dispatch import receiver
from phonenumber_field.modelfields import PhoneNumberField

# Create your models here.
class User(AbstractBaseUser, PermissionsMixin):
    """
    Custom User model extending Django's AbstractUser
    """
    user_id = models.AutoField(primary_key=True)
    username = models.CharField(
        max_length=50,
        unique=True,
        verbose_name=_('Username')
    )
    full_name = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name=_('Full Name')
    )
    email = models.EmailField(
        max_length=255,
        unique=True,
        validators=[EmailValidator()],
        verbose_name=_('Email Address')
    )
    phone = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name=_('Phone Number')
    )
    address = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('Address')
    )
    email_verified = models.BooleanField(
        default=False,
        verbose_name=_('Email Verified')
    )
    created_at = models.DateTimeField(
        default=timezone.now,
        verbose_name=_('Created At')
    )

    # Django-specific fields for admin and Authentication
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    # Specify which field is used for login
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta:
        """
        Metadata for User model
        Defines database table name and ordering
        """
        db_table = 'users'
        ordering = ['-created_at']
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def __str__(self):
        # String representation of the user returns email or username
        return self.email or self.username
    
    def get_full_name(self):
        # Return the full name of the user
        return self.full_name or self.username
    
    def get_short_name(self):
        # Return the short name for the user
        return self.username
    
    def has_sufficient_credits(self, required_credits):
        # Check if user has enough credits for an SMS transaction
        return self.credits >= required_credits
    
    def update_credits(self, amount, transaction_type='manual'):
        # Update user's credit balance and log the tramsaction
        from transactions.models import CreditTransaction

        # Update credit balance
        self.credits += amount
        self.save()

        # Log the credit transaction
        CreditTransaction.objects.create(
            user=self,
            transaction_type=transaction_type,
            credits=abs(amount),
            amount=abs(amount)
        )

class Profile(models.Model):
    """
    Extended User profile model
    Stores additional user information not suitable for the main User model
    """
    profile_id = models.AutoField(
        primary_key=True,
        verbose_name=_('Profile ID')
    )
    profile_picture = models.CharField(
        max_length=500,
        blank=True,
        null=True,
        verbose_name=_('Profile Picture Path')
    )
    users_user_id = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        db_column='users_user_id',
        verbose_name=_('User')
    )

    class Meta:
        """
        Metadata for Profile model
        Defines database table name and ordering
        """
        db_table = 'profiles'
        verbose_name = 'Profile'
        verbose_name_plural = 'Profiles'

    def __str__(self):
        """
        String representation of the profile
        Returns username of the associated user
        """
        return f"Profile for {self.users_user_id.username}"
    
    def get_profile_picture_url(self):
        """
        Retrieve the profile picture URL
        Returns URL of the profile picture if exists
        None if no profile picture
        """
        return self.profile_picture if self.profile_picture else None
    

class TwoFactorAuth(models.Model):
    """
    Two-Factor Authentication configuration
    Allows users to enable additional account security
    """
    auth_id = models.AutoField(primary_key=True)
    user_id = models.OneToOneField(
        User,
        on_delete=models.CASCADE
    )
    secret_key = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )
    is_enabled = models.BooleanField(default=False)
    last_verified = models.DateTimeField(
        null=True,
        blank=True
    )

    def __str__(self):
        """
        String representation for admin and debugging
        """
        return f"2FA for {self.user.username}"
    
    def generate_secret_key(self):
        """
        Generate a new secret key for two-factor authentication
        Returns Base32 encoded secret key
        """
        import pyotp
        self.secret_key = pyotp.random_base32()
        self.save()
        return self.secret_key
    
    def verify_totp(self, token):
        """
        Verify a a Time-based One-Time Password (TOTP)
        One-time token provided by user
        Returns True if token is valid, False otherwise
        """
        import pyotp
        totp = pyotp.TOTP(self.secret_key)
        return totp.verify(token)
    

# Signal to create profile automatically when user is created and 2FA creation
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Automatically create a profile and TwoFactorAuth when a new user is created
    Ensures each User has a corresponding Profile and TwoFactorAuth instance
    """
    if created:
        Profile.objects.create(users_user_id=instance)
        TwoFactorAuth.objects.create(user_id=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """
    Ensure profile and TwoFactorAuth are saved when User is updated
    Handles cases where profile or TwoFactorAuth might not exist
    """
    try:
        instance.profile.save()
        instance.twofactorauth.save()
    except (Profile.DoesNotExist, TwoFactorAuth.DoesNotExist):
        Profile.objects.create(users_user_id=instance)
        TwoFactorAuth.objects.create(user_id=instance)