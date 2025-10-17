from django.db import models
from pets. models import PetProfile
from django.conf import settings
from django.utils import timezone
from django.contrib.auth.models import User
from accounts.models import CustomUser
from appointments.models import Appointment


class MedicalRecord(models.Model):
    pet = models.ForeignKey(PetProfile, on_delete=models.CASCADE, related_name='medical_records')
    appointment = models.ForeignKey(Appointment, on_delete=models.CASCADE, null=True, blank=True)
    vet = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='vet_records')
    diagnosis = models.TextField()
    treatment = models.TextField()
    date = models.DateField(auto_now_add=True)
    prescription = models.TextField(blank=True)
    visit_date = models.DateTimeField(default=timezone.now, editable=False)
    follow_up_date = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"Record for {self.pet.name} ({self.date})"
