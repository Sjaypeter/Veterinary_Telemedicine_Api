from django.db import models
from datetime import datetime
import uuid
from django.contrib.auth.models import User
# Create your models here.

#Models are  Vetprofile, Ownerprofile,Pets, Appointments, Medical_records

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


    
class PetProfile(models.Model):
    owner = models.ForeignKey(OwnerProfile, on_delete=models.CASCADE, related_name="pets")
    name = models.CharField(max_length=100)
    species = models.CharField(max_length=100, blank=True)
    breed = models.CharField(max_length=100, blank=True)
    age = models.IntegerField()
    
    def __str__(self):
        return f"{self.name} - {self.species}"



class Appointment(models.Model):
    owner = models.ForeignKey(OwnerProfile, on_delete=models.CASCADE, related_name="appointments")
    vet = models.ForeignKey(Vetprofile, on_delete=models.CASCADE, related_name="appointments")
    pet = models.ForeignKey(PetProfile, on_delete=models.CASCADE, related_name="appointments")
    scheduled_date = models.DateTimeField()
    reason = models.TextField()
    status = models.CharField(max_length=20, choices=[
        ("pending","Pending"),
        ("confirmed", "Confirmed"),
        ("completed", "Completed"),
        ("canceled", "Canceled"),
    ], default="pending")
    
    
    def __str__(self):
        return f"Appointment for {self.pet.name} with Dr. {self.vet.user.username}"



class MedicalRecord(models.Model):
   pet = models.ForeignKey(PetProfile, on_delete=models.CASCADE, related_name="medical_records")
   vet = models.ForeignKey(Vetprofile, on_delete=models.CASCADE, related_name="medical_records")
   diagnosis = models.TextField()
   treatment = models.TextField()
   date = models.DateTimeField(auto_now_add=True)
   
   def __str__(self):
       return f"Record for {self.pet.name} - {self.date.strftime('%Y:%m:%d')}"
    
