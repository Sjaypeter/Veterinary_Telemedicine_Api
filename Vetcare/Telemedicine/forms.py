from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth.models import User
from django.forms import EmailField, CharField
from . models import OwnerProfile, Vetprofile, PetProfile, Appointment, MedicalRecord
from django.db import models
from django.core.exceptions import ValidationError
from django import forms


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

class OwnerProfileForm(forms.ModelForm):
    

