from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError

from accounts.models import CustomUser
from pets.models import PetProfile


class Appointment(models.Model):
    """Model to handle veterinary appointments between clients and veterinarians. """
    
    # Status choices
    PENDING = 'pending'
    CONFIRMED = 'confirmed'
    COMPLETED = 'completed'
    CANCELLED = 'cancelled'
    
    STATUS_CHOICES = [
        (PENDING, 'Pending'),
        (CONFIRMED, 'Confirmed'),
        (COMPLETED, 'Completed'),
        (CANCELLED, 'Cancelled'),
    ]
    
    # Relationships
    client = models.ForeignKey(CustomUser,on_delete=models.CASCADE,related_name='client_appointments',limit_choices_to={'role': 'CLIENT'},help_text="Pet owner requesting the appointment")
    veterinarian = models.ForeignKey(CustomUser,on_delete=models.CASCADE,related_name='vet_appointments',limit_choices_to={'role': 'VETERINARIAN'},help_text="Veterinarian assigned to the appointment")
    pet = models.ForeignKey(PetProfile,on_delete=models.CASCADE,related_name='appointments',help_text="Pet for the appointment")
    
    # Appointment details
    date = models.DateField(default=timezone.now,help_text="Appointment date")
    time = models.TimeField(null=True,blank=True,help_text="Appointment time (optional until confirmed)")
    reason = models.TextField(help_text="Reason for the appointment")
    status = models.CharField( max_length=20,choices=STATUS_CHOICES,default=PENDING,db_index=True)
    notes = models.TextField( blank=True, help_text="Additional notes or special instructions")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Appointment'
        verbose_name_plural = 'Appointments'
        ordering = ['-date', '-created_at']
        indexes = [
            models.Index(fields=['date', 'status']),
            models.Index(fields=['client', 'date']),
            models.Index(fields=['veterinarian', 'date']),
        ]
    
    def __str__(self):
        return f"{self.pet.name} - {self.date} ({self.get_status_display()})"
    
    def clean(self):
        """Validate appointment data"""
        super().clean()
        
        # Ensure client and veterinarian are different users
        if self.client == self.veterinarian:
            raise ValidationError("Client and veterinarian cannot be the same user.")
        
        # Ensure pet belongs to client
        if self.pet and self.pet.owner != self.client:
            raise ValidationError("The selected pet does not belong to this client.")
        
        # Ensure appointment date is not in the past (for new appointments)
        if not self.pk and self.date < timezone.now().date():
            raise ValidationError("Appointment date cannot be in the past.")
    
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
    
    @property
    def is_past(self):
        """Check if appointment date has passed"""
        return self.date < timezone.now().date()
    
    @property
    def is_upcoming(self):
        """Check if appointment is upcoming and confirmed"""
        return self.date >= timezone.now().date() and self.status == self.CONFIRMED
    
    @property
    def can_be_cancelled(self):
        """Check if appointment can be cancelled"""
        return self.status in [self.PENDING, self.CONFIRMED] and not self.is_past


class Consultation(models.Model):
    """Model to store consultation details after an appointment is completed."""
    
    # Relationships
    appointment = models.OneToOneField(Appointment,on_delete=models.CASCADE,related_name='consultation',help_text="Associated appointment")
    veterinarian = models.ForeignKey(CustomUser,on_delete=models.CASCADE,related_name='consultations',limit_choices_to={'role': 'VETERINARIAN'},
        help_text="Veterinarian who conducted the consultation"
    )
    
    # Consultation details
    diagnosis = models.TextField(help_text="Diagnosis from the consultation")
    symptoms = models.TextField(blank=True,help_text="Symptoms observed during consultation")
    notes = models.TextField(help_text="Detailed consultation notes")
    prescription = models.TextField(blank=True,help_text="Prescribed medications or treatments")
    follow_up_required = models.BooleanField(default=False,help_text="Whether a follow-up appointment is needed")
    follow_up_date = models.DateField(null=True,blank=True,help_text="Recommended follow-up date")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Consultation'
        verbose_name_plural = 'Consultations'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['veterinarian', 'created_at']),
            models.Index(fields=['appointment']),
        ]
    
    def __str__(self):
        return f"Consultation for {self.appointment.pet.name} on {self.created_at.strftime('%Y-%m-%d')}"
    
    def clean(self):
        """Validate consultation data"""
        super().clean()
        
        # Ensure appointment is completed
        if self.appointment.status != Appointment.COMPLETED:
            raise ValidationError("Consultation can only be created for completed appointments.")
        
        # Ensure veterinarian matches appointment veterinarian
        if self.veterinarian != self.appointment.veterinarian:
            raise ValidationError("Consultation veterinarian must match appointment veterinarian.")
        
        # Validate follow-up date
        if self.follow_up_required and not self.follow_up_date:
            raise ValidationError("Follow-up date is required when follow-up is needed.")
        
        if self.follow_up_date and self.follow_up_date <= timezone.now().date():
            raise ValidationError("Follow-up date must be in the future.")
    
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
    
    @property
    def client(self):
        """Get the client from the associated appointment"""
        return self.appointment.client
    
    @property
    def pet(self):
        """Get the pet from the associated appointment"""
        return self.appointment.pet