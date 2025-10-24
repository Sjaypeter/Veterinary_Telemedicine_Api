from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError

from pets.models import PetProfile
from accounts.models import CustomUser
from appointments.models import Appointment


class MedicalRecord(models.Model):
    """
    Model to store medical records for pets after veterinary visits.
    Links to appointments and consultations for comprehensive tracking.
    """
    
    # Relationships
    pet = models.ForeignKey(PetProfile,on_delete=models.CASCADE,related_name='medical_records',help_text="Pet this record belongs to")
    appointment = models.ForeignKey(Appointment,on_delete=models.SET_NULL,null=True,blank=True,related_name='medical_records',help_text="Associated appointment (if applicable)")
    veterinarian = models.ForeignKey(CustomUser,on_delete=models.SET_NULL, null=True, blank=True,
        limit_choices_to={'role': 'VETERINARIAN'},
        related_name='medical_records',
        help_text="Veterinarian who created this record"
    )
    visit_date = models.DateTimeField(default=timezone.now,help_text="Date and time of the online consultation")
    diagnosis = models.TextField(help_text="Medical diagnosis")
    symptoms = models.TextField(blank=True,help_text="Observed symptoms")
    treatment = models.TextField(help_text="Treatment provided or recommended")
    prescription = models.TextField(blank=True,help_text="Medications prescribed")
    follow_up_required = models.BooleanField(default=False,help_text="Whether a follow-up consultation is needed")
    follow_up_date = models.DateField(null=True,blank=True,help_text="Scheduled follow-up date")
    notes = models.TextField(blank=True,help_text="Additional notes or observations" )
    weight = models.DecimalField(max_digits=6,decimal_places=2,null=True,blank=True,help_text="Pet weight in kg at time of visit")
    temperature = models.DecimalField(max_digits=4,decimal_places=1,null=True,blank=True,help_text="Body temperature in Celsius")

    test_results = models.FileField(upload_to='medical_records/tests/%Y/%m/',null=True,blank=True,help_text="Lab test results or medical documents")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Medical Record'
        verbose_name_plural = 'Medical Records'
        ordering = ['-visit_date', '-created_at']
        indexes = [
            models.Index(fields=['pet', 'visit_date']),
            models.Index(fields=['veterinarian', 'visit_date']),
            models.Index(fields=['appointment']),
        ]
    
    def __str__(self):
        return f"Medical Record: {self.pet.name} - {self.visit_date.strftime('%Y-%m-%d')}"
    
    def clean(self):
        """Validate medical record data"""
        super().clean()
        
        # Ensure follow-up date is provided if follow-up is required
        if self.follow_up_required and not self.follow_up_date:
            raise ValidationError({
                "follow_up_date": "Follow-up date is required when follow-up is needed."
            })
        
        # Ensure follow-up date is in the future
        if self.follow_up_date and self.follow_up_date <= timezone.now().date():
            raise ValidationError({
                "follow_up_date": "Follow-up date must be in the future."
            })
        
        # Ensure appointment matches pet if appointment is provided
        if self.appointment and self.appointment.pet != self.pet:
            raise ValidationError({
                "appointment": "The appointment must be for the same pet as this medical record."
            })
        
        # Ensure veterinarian matches appointment if both are provided
        if self.appointment and self.veterinarian and self.appointment.veterinarian != self.veterinarian:
            raise ValidationError({
                "veterinarian": "The veterinarian must match the appointment veterinarian."
            })
    
    def save(self, *args, **kwargs):
        """Validate before saving"""
        self.full_clean()
        super().save(*args, **kwargs)
    
    @property
    def pet_owner(self):
        """Get the pet owner"""
        return self.pet.owner
    
    @property
    def is_follow_up_pending(self):
        """Check if follow-up is due"""
        if not self.follow_up_required or not self.follow_up_date:
            return False
        return self.follow_up_date >= timezone.now().date()
    
    @property
    def days_until_follow_up(self):
        """Calculate days until follow-up"""
        if not self.follow_up_date:
            return None
        delta = self.follow_up_date - timezone.now().date()
        return delta.days
