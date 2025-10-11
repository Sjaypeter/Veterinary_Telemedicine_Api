from django.db import models
from django.conf import settings
from django.contrib.auth.models import User




#This ensures that Django always points to my active user model — whether it’s the default one or a custom one
User = settings.AUTH_USER_MODEL 

# Create your models here.


class PetProfile(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="pets")
    name = models.CharField(max_length=100)
    species = models.CharField(max_length=100, blank=True)
    breed = models.CharField(max_length=100, blank=True)
    age = models.IntegerField()
    gender = models.CharField(max_length=10, choices=[
        ('male', 'Male'),
        ('female', 'Female'),
    ])
    weight = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    profile_image = models.ImageField(upload_to='pets/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.name} - {self.owner.username}"
    
    
