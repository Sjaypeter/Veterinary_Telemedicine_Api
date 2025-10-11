from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.contrib.auth.models import User
# Create your models here.

#Models are  Vetprofile, Ownerprofile,Pets, Appointments, Medical_records

#This ensures that Django always points to my active user model — whether it’s the default one or a custom one
User = settings.AUTH_USER_MODEL 



class CustomUser(AbstractUser):
    is_vet = models.BooleanField(default=False)
    is_owner = models.BooleanField(default=False)
    bio = models.TextField(blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profiles/', blank=True, null=True)
    following = models.ManyToManyField('self', symmetrical=False, related_name='followers', blank=True)

    def __str__(self):
        return self.username

class OwnerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=15)
    address = models.TextField()
    
    def __str__(self):
        return f"Owner: {self.user.username}"


class Vetprofile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    specialization = models.CharField(max_length=100)
    license_number = models.CharField(max_length=50)
    
    def __str__(self):
        return f"Vet: {self.user.username} - {self.specialization}"
