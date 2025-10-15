from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.contrib.auth.models import User
# Create your models here.

class CustomUser(AbstractUser):
    ROLES = (
        ('veterinarian', 'Veterinarian'),
        ('client', 'Client'),
    )
    role = models.CharField(max_length=12, choices=ROLES)

    def __str__(self):
        return f"{self.username} ({self.role})"

class OwnerProfile(models.Model):
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
