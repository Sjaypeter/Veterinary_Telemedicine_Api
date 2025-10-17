from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.core.validators import RegexValidator


class CustomUserManager(BaseUserManager):
    """Custom user manager for email-based authentication"""

    def create_user(self, email, password=None, **extra_fields):
        """Create and save a regular user with email and password"""
        if not email:
            raise ValueError("The Email field must be set")
        
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """Create and save a superuser with email and password"""
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(email, password, **extra_fields)


class CustomUser(AbstractUser):
    """Custom user model with email authentication and role-based access"""
    
    VETERINARIAN = 'VETERINARIAN'
    CLIENT = 'CLIENT'
    
    ROLE_CHOICES = (
        (VETERINARIAN, 'Veterinarian'),
        (CLIENT, 'Client'),
    )
    
    # Remove username, use email instead
    username = None
    email = models.EmailField(unique=True, db_index=True)
    role = models.CharField(
        max_length=15, 
        choices=ROLE_CHOICES, 
        default=CLIENT,
        db_index=True
    )
    
    # Additional fields
    first_name = models.CharField(max_length=150, blank=True)
    last_name = models.CharField(max_length=150, blank=True)
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
    )
    phone = models.CharField(
        validators=[phone_regex], 
        max_length=17, 
        blank=True,
        help_text="Contact phone number"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.email} ({self.get_role_display()})"
    
    def get_full_name(self):
        """Return the user's full name"""
        return f"{self.first_name} {self.last_name}".strip() or self.email
    
    @property
    def is_veterinarian(self):
        """Check if user is a veterinarian"""
        return self.role == self.VETERINARIAN
    
    @property
    def is_client(self):
        """Check if user is a client"""
        return self.role == self.CLIENT


class ClientProfile(models.Model):
    """Extended profile information for clients/pet owners"""
    
    user = models.OneToOneField(
        CustomUser, 
        on_delete=models.CASCADE,
        related_name='client_profile',
        limit_choices_to={'role': CustomUser.CLIENT}
    )
    address = models.TextField(blank=True)
    emergency_contact = models.CharField(max_length=17, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Client Profile'
        verbose_name_plural = 'Client Profiles'
    
    def __str__(self):
        return f"Client: {self.user.get_full_name() or self.user.email}"


class Vetprofile(models.Model):
    user = models.OneToOneField(
        CustomUser, 
        on_delete=models.CASCADE,
        related_name='vet_profile',
        limit_choices_to={'role': CustomUser.VETERINARIAN}
    )
    specialization = models.CharField(
        max_length=100,
        help_text="e.g., Surgery, Internal Medicine, Dentistry"
    )
    license_number = models.CharField(
        max_length=50, 
        unique=True,
        help_text="Professional license number"
    )
    # Add these new fields:
    years_of_experience = models.PositiveIntegerField(default=0)
    bio = models.TextField(blank=True, help_text="Professional biography")
    is_available = models.BooleanField(
        default=True,
        help_text="Available for appointments"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Veterinarian Profile'
        verbose_name_plural = 'Veterinarian Profiles'
        ordering = ['user__email']
    
    def __str__(self):
        return f"Vet: {self.user.get_full_name() or self.user.email} - {self.specialization}"