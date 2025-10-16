from django.db import models
from datetime import datetime
from django.conf import settings
from django.contrib.auth.models import User
from pets .models import PetProfile


#Handles appointment and consultations

#This ensures that Django always points to my active user model — whether it’s the default one or a custom one
User = settings.AUTH_USER_MODEL 

# Create your models here.
class Appointment(models.Model):
    client = models.ForeignKey(User, on_delete=models.CASCADE, related_name="appointments")
    veterinarian = models.ForeignKey(User, on_delete=models.CASCADE, related_name="vet_appointments")
    pet = models.ForeignKey(PetProfile, on_delete=models.CASCADE, related_name="appointments")
    appointment_date = models.DateTimeField()
    reason = models.TextField()
    status = models.CharField(max_length=20, choices=[
        ("pending","Pending"),
        ("confirmed", "Confirmed"),
        ("completed", "Completed"),
        ("canceled", "Canceled"),
    ], default="pending")
    
    
    def __str__(self):
        return f"{self.pet.name} - {self.date.strftime('%Y-%m-%d %H:%M')}"
    

class Consultation(models.Model):
    client = models.ForeignKey(User, on_delete=models.CASCADE,null=True, blank=True)
    appointment = models.OneToOneField(Appointment, on_delete=models.CASCADE, related_name='consultation')
    notes = models.TextField()
    prescription = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Consultation for {self.appointment.pet.name}"