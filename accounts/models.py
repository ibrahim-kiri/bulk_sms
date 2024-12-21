from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser, PermissionsMixin
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.db.models.signals import post_save
from django.dispatch import receiver
from phonenumber_field.modelfields import PhoneNumberField

# Create your models here.
class CustomUserManager(BaseUserManager):
    def create_user(self, username, email=None, password=None, **extra_fields):
        if not username:
            raise ValueError('Users must have a username')
        
        user = self.model(
            username=username,
            email=email,
            **extra_fields
        )

        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, username, email=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        
        return self.create_user(username, email, password, **extra_fields)
    
    def get_by_natural_key(self, username):
        return self.get(username=username)

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
        blank=True,
        null=True,
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
    created_at = models.DateTimeField(
        default=timezone.now,
        verbose_name=_('Created At')
    )

    # Django-specific fields for admin and Authentication
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)


    # Specify which field is used for login
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

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
        return self.username
    
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
    
# Signal to create profile automatically when user is created
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Automatically creates a profile when a new user is created
    """
    if created:
        Profile.objects.create(users_user_id=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """
    Ensure profile is saved when user is updated
    """
    try:
        instance.profile.save()
    except Profile.DoesNotExist:
        Profile.objects.create(users_user_id=instance)

    