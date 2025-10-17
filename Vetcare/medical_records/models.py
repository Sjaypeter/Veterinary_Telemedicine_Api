from django.db import models
from pets. models import PetProfile
from django.conf import settings
from django.utils import timezone

User = settings.AUTH_USER_MODEL

class MedicalRecord(models.Model):
    pet = models.ForeignKey(PetProfile, on_delete=models.CASCADE, related_name='medical_records')
    vet = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='vet_records')
    diagnosis = models.TextField()
    treatment = models.TextField()
    date = models.DateField(auto_now_add=True)
    prescription = models.TextField(blank=True)
    visit_date = models.DateTimeField(default=timezone.now, editable=False)
    follow_up_date = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"Record for {self.pet.name} ({self.date})"
