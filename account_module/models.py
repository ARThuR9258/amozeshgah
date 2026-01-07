from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils.translation import gettext_lazy as _


class UserManager(BaseUserManager):
    """Custom user model manager where phone_number is the unique identifier"""
    
    def create_user(self, phone_number, password=None, **extra_fields):
        """Create and save a user with the given phone_number and password."""
        if not phone_number:
            raise ValueError(_('The Phone Number must be set'))
        
        # Generate a unique username if not provided
        if not extra_fields.get('username'):
            extra_fields['username'] = f"user_{phone_number}"
        
        user = self.model(phone_number=phone_number, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, phone_number, password=None, **extra_fields):
        """Create and save a SuperUser with the given phone_number and password."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('is_verified', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))
        
        # Ensure first_name and last_name are provided
        if not extra_fields.get('first_name') or not extra_fields.get('last_name'):
            raise ValueError(_('Superuser must have first_name and last_name.'))
            
        return self.create_user(phone_number, password, **extra_fields)


class User(AbstractUser):
    email = models.EmailField(unique=True, null=True, blank=True, verbose_name='ایمیل')
    phone_number = models.CharField(max_length=11, unique=True, verbose_name='شماره موبایل')
    is_verified = models.BooleanField(default=False, verbose_name='تایید شده')
    
    # Make username non-required and email not used for authentication
    username = models.CharField(max_length=150, unique=True, null=True, blank=True, verbose_name='نام کاربری')
    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = ['first_name', 'last_name']
    
    objects = UserManager()

    class Meta:
        verbose_name = 'کاربر'
        verbose_name_plural = 'کاربران'

    def __str__(self):
        return self.phone_number or self.email or self.username
