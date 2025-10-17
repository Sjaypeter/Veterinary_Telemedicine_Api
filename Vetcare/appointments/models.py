from django.db import models
from datetime import datetime
from django.conf import settings
from django.contrib.auth.models import User
from pets .models import PetProfile
from accounts.models import CustomUser
from django.utils import timezone


#Handles appointment and consultations


# Create your models here.
class Appointment(models.Model):
    client = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="appointments")
    veterinarian = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="vet_appointments")
    pet = models.ForeignKey(PetProfile, on_delete=models.CASCADE, related_name="appointments", null=True, blank=True)
    date = models.DateField(default=timezone.now)

    reason = models.TextField()
    status = models.CharField(max_length=20, choices=[
        ("pending","Pending"),
        ("confirmed", "Confirmed"),
        ("completed", "Completed"),
        ("canceled", "Canceled"),
    ], default="pending")
    
    
    def __str__(self):
        return f"{self.pet} - {self.date.strftime('%Y-%m-%d %H:%M')}"
    

class Consultation(models.Model):
    client = models.ForeignKey(CustomUser,on_delete=models.CASCADE,null=True, blank=True)
    appointment = models.OneToOneField(Appointment, on_delete=models.CASCADE, related_name='consultation')
    notes = models.TextField()
    prescription = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Consultation for {self.appointment.pet.name}"