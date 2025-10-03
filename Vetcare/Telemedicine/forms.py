from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.forms import EmailField, CharField
from . models import OwnerProfile, Vetprofile, PetProfile, Appointment, MedicalRecord
from django.db import models
from django.core.exceptions import ValidationError
from django import forms
from django.utils import timezone

#This is a usercreation form for the register view and it validates the email and first&lastnames
class CustomUserCreationForm(UserCreationForm):
    email = EmailField(label=_("Email address"), required=True, help_text=_("Required."))
    first_name = CharField(label=_("First name"), max_length=150, required=True)
    last_name = CharField(label=_("Last name"), max_length=150, required=True)
    
    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]
    
    def clean_email(self):
        email = self.cleaned_data.get("email")
        if User.objects.filter(email=email).exists():
            raise ValidationError("This email is already in use. Please use a different email.")
        return email    
        
    def save(self, commit = True):
        user = super(UserCreationForm, self).save(commit=False)
        user.email = self.cleaned_data["email"]
        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]
        
        if commit:
            user.save()
        return user
        

class OwnerProfileForm(forms.ModelForm):
    class Meta:
        model = OwnerProfile
        fields = ["phone", "address"]
        
        
    def clean_phone(self):
        phone = self.cleaned_data.get("phone")
        if not phone.isdigit():
            raise forms.ValidationError("Phone number must contain only digits.")
        if len(phone) <15:
            raise forms.ValidationError("Phone number must be at least 15 digits long.")
        return phone


    
class VetprofileForm(forms.ModelForm):
    class Meta:
        model = Vetprofile
        fields = ["specialization", "license_number"]
        
    def clean_license_number(self):
        license_number = self.cleaned_data.get("license_number")
        if len(license_number) < 5:
            raise forms.ValidationError("License number must be at least 5 charcters long.")
        return license_number
    
    
        
class PetProfileForm(forms.ModelForm):
    class Meta:
        model = PetProfile
        fields = ["owner", "name", "species", "breed", "age"]
        
    def clean_age(self):
        age = self.cleaned_data.get("age")
        if age < 0:
            raise forms.ValidationError("Age cannot be negative")
        
        if age > 50:
            raise forms.ValidationError("Age seems too high for a pet. Please check again")
        return age
        
        
class AppointmentForm(forms.ModelForm):
    model = Appointment
    fields = ["owner","vet","pet", "reason","status","scheduled_date"]
    
    def clean_scheduled_date(self):
        scheduled_date = self.cleaned_data.get("scheduled_date")
        if scheduled_date < timezone.now():
            raise forms.ValidationError("Appointment date cannot be in the past")
        return scheduled_date
    
    
    
class MedicalRecordForm(forms.ModelForm):
    model = MedicalRecord
    fields = ["pet", "vet", "diagnosis", "treatment"]
    
    def clean_diagnosis(self):
        diagnosis = self.cleaned_data.get("diagnosis")
        if len(diagnosis.strip()) < 5:
            raise forms.ValidationError("Diagnosis is too short. Please provide more details")
        return diagnosis
    
    def clean_treatment(self):
        treatment = self.cleaned_data.get("treatment")
        if len(treatment.strip()) < 5:
            raise forms.ValidationError("Treatment details are too short. Please provide more info")
        return treatment

