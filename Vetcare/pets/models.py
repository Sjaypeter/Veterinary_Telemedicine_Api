from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError

from accounts.models import CustomUser


class PetProfile(models.Model):

    MALE = 'Male'
    FEMALE = 'Female'
    UNKNOWN = 'Unknown'
    
    GENDER_CHOICES = [
        (MALE, 'Male'),
        (FEMALE, 'Female'),
        (UNKNOWN, 'Unknown'),
    ]
    
    # Common species choices
    DOG = 'Dog'
    CAT = 'Cat'
    BIRD = 'Bird'
    RABBIT = 'Rabbit'
    HAMSTER = 'Hamster'
    GUINEA_PIG = 'Guinea Pig'
    REPTILE = 'Reptile'
    FISH = 'Fish'
    OTHER = 'Other'
    
    SPECIES_CHOICES = [
        (DOG, 'Dog'),
        (CAT, 'Cat'),
        (BIRD, 'Bird'),
        (RABBIT, 'Rabbit'),
        (HAMSTER, 'Hamster'),
        (GUINEA_PIG, 'Guinea Pig'),
        (REPTILE, 'Reptile'),
        (FISH, 'Fish'),
        (OTHER, 'Other'),
    ]
    
    owner = models.ForeignKey(CustomUser,on_delete=models.CASCADE,related_name='pets',limit_choices_to={'role': 'CLIENT'},help_text="Pet owner")
    name = models.CharField(max_length=100,help_text="Pet's name")
    species = models.CharField(max_length=100,choices=SPECIES_CHOICES,default=OTHER,help_text="Type of animal")
    breed = models.CharField(max_length=100,blank=True,help_text="Breed (optional)")
    gender = models.CharField(max_length=10,choices=GENDER_CHOICES,default=UNKNOWN,help_text="Pet's gender")
    date_of_birth = models.DateField(null=True,blank=True,help_text="Pet's date of birth")
    age = models.PositiveIntegerField(null=True,blank=True,validators=[MinValueValidator(0), MaxValueValidator(50)],help_text="Age in years (if date of birth is unknown)"
    )
    weight = models.DecimalField( max_digits=6, decimal_places=2, null=True, blank=True, validators=[MinValueValidator(0.01)], help_text="Weight in kilograms")
    color = models.CharField(max_length=100,blank=True,help_text="Pet's color/markings")
    microchip_number = models.CharField(max_length=50,blank=True,unique=True,null=True,help_text="Microchip identification number")
    allergies = models.TextField(blank=True,help_text="Known allergies")
    medical_conditions = models.TextField(blank=True,help_text="Existing medical conditions")
    current_medications = models.TextField(blank=True,help_text="Current medications")
    profile_image = models.ImageField(upload_to='pets/profiles/%Y/%m/',blank=True,null=True,help_text="Pet's photo")
    notes = models.TextField(blank=True,help_text="Additional notes about the pet")
    is_active = models.BooleanField( default=True, help_text="Whether this pet is still under care")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Pet Profile'
        verbose_name_plural = 'Pet Profiles'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['owner', 'is_active']),
            models.Index(fields=['species']),
            models.Index(fields=['microchip_number']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.species}) - {self.owner.get_full_name() or self.owner.email}"
    
    def clean(self):
        """Validate pet data"""
        super().clean()
        
        # Ensure either date_of_birth or age is provided
        if not self.date_of_birth and not self.age:
            raise ValidationError(
                "Either date of birth or age must be provided."
            )
        
        # Validate date of birth is not in the future
        if self.date_of_birth and self.date_of_birth > timezone.now().date():
            raise ValidationError({
                "date_of_birth": "Date of birth cannot be in the future."
            })
        
        # Ensure microchip is unique if provided
        if self.microchip_number:
            existing = PetProfile.objects.filter(
                microchip_number=self.microchip_number
            ).exclude(pk=self.pk)
            if existing.exists():
                raise ValidationError({
                    "microchip_number": "This microchip number is already registered."
                })
    
    def save(self, *args, **kwargs):
        """Calculate age from date of birth if not provided"""
        if self.date_of_birth and not self.age:
            today = timezone.now().date()
            age_in_days = (today - self.date_of_birth).days
            self.age = age_in_days // 365
        
        self.full_clean()
        super().save(*args, **kwargs)
    
    @property
    def calculated_age(self):
        """Calculate current age from date of birth"""
        if self.date_of_birth:
            today = timezone.now().date()
            age_in_days = (today - self.date_of_birth).days
            years = age_in_days // 365
            months = (age_in_days % 365) // 30
            return f"{years} years, {months} months"
        return f"{self.age} years" if self.age else "Unknown"
    
    @property
    def has_medical_conditions(self):
        """Check if pet has any medical conditions"""
        return bool(self.medical_conditions or self.allergies)
    
    @property
    def needs_attention(self):
        """Check if pet needs medical attention (has conditions or medications)"""
        return bool(
            self.medical_conditions or 
            self.allergies or 
            self.current_medications
        )