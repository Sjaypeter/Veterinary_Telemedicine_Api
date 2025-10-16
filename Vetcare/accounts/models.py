from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.conf import settings
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
# Create your models here.


class Role(models.TextChoices):
    VET = 'VET', 'vet'
    CLIENT = 'CLIENT', 'client'




class CustomUser(AbstractBaseUser):
    email = models.EmailField(unique=True)
    bio = models.TextField(blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    is_vet = models.BooleanField(default=False)
    is_client = models.BooleanField(default=False)
    role = models.CharField(max_length=20, choices=[('vet', 'Vet'), ('client', 'Client')], default='client',)


    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.email

class ClientProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    phone = models.CharField(max_length=15)
    address = models.TextField()
    
    def __str__(self):
        return f"Owner: {self.user.username}"


class Vetprofile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    specialization = models.CharField(max_length=100)
    license_number = models.CharField(max_length=50)
    
    def __str__(self):
        return f"Vet: {self.user.username} - {self.specialization}"
