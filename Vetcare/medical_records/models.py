from django.db import models
from pets.models import PetProfile

class MedicalRecord(models.Model):
    pet = models.ForeignKey(PetProfile, on_delete=models.CASCADE, related_name='medical_records')
    diagnosis = models.TextField()
    treatment = models.TextField()
    date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"Record for {self.pet.name} ({self.date})"


class Vaccination(models.Model):
    pet = models.ForeignKey(PetProfile, on_delete=models.CASCADE, related_name='vaccinations')
    vaccine_name = models.CharField(max_length=100)
    date_given = models.DateField()
    next_due_date = models.DateField(blank=True, null=True)

    def __str__(self):
        return f"{self.vaccine_name} - {self.pet.name}"