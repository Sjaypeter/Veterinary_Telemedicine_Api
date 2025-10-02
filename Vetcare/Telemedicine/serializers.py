from rest_framework import serializers
from . models import OwnerProfile, PetProfile, Appointment, MedicalRecord, Vetprofile

class OwnerProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = OwnerProfile
        fields = "__all__"
        
class VetprofileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vetprofile
        fields = "__all__"
    
        
class PetProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = PetProfile
        fields = "__all__"
        
class AppointmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Appointment
        fields = "__all__"       
        
        
class MedicalRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = MedicalRecord
        fields = "__all__"