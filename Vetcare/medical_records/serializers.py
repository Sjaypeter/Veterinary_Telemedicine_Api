from rest_framework import serializers
from django.utils import timezone

from .models import MedicalRecord
from appointments.models import Appointment
from pets.models import PetProfile


class MedicalRecordListSerializer(serializers.ModelSerializer):
    pet_name = serializers.CharField(source='pet.name', read_only=True)
    pet_species = serializers.CharField(source='pet.species', read_only=True)
    pet_owner_name = serializers.CharField(source='pet_owner.get_full_name', read_only=True)
    vet_name = serializers.CharField(source='veterinarian.get_full_name', read_only=True)
    
    class Meta:
        model = MedicalRecord
        fields = [
            'id', 'pet', 'pet_name', 'pet_species', 'pet_owner_name',
            'veterinarian', 'vet_name', 'visit_date', 'diagnosis',
            'follow_up_required', 'follow_up_date', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class MedicalRecordDetailSerializer(serializers.ModelSerializer):

    pet_name = serializers.CharField(source='pet.name', read_only=True)
    pet_species = serializers.CharField(source='pet.species', read_only=True)
    pet_breed = serializers.CharField(source='pet.breed', read_only=True)
    pet_owner_name = serializers.CharField(source='pet_owner.get_full_name', read_only=True)
    pet_owner_email = serializers.EmailField(source='pet_owner.email', read_only=True)
    
    vet_name = serializers.CharField(source='veterinarian.get_full_name', read_only=True)
    vet_email = serializers.EmailField(source='veterinarian.email', read_only=True)
    
    appointment_date = serializers.DateField(source='appointment.date', read_only=True)
    
    is_follow_up_pending = serializers.BooleanField(read_only=True)
    days_until_follow_up = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = MedicalRecord
        fields = [
            'id', 'pet', 'pet_name', 'pet_species', 'pet_breed',
            'pet_owner_name', 'pet_owner_email',
            'appointment', 'appointment_date',
            'veterinarian', 'vet_name', 'vet_email',
            'visit_date', 'diagnosis', 'symptoms', 'treatment',
            'prescription', 'follow_up_required', 'follow_up_date',
            'notes', 'weight', 'temperature', 'test_results',
            'is_follow_up_pending', 'days_until_follow_up',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class MedicalRecordCreateSerializer(serializers.ModelSerializer):
    appointment_id = serializers.PrimaryKeyRelatedField(
        queryset=Appointment.objects.filter(status='completed'),
        source='appointment',
        write_only=True,
        required=False,
        help_text="Optional: Link to a completed appointment"
    )
    pet = serializers.PrimaryKeyRelatedField(queryset=PetProfile.objects.all(),help_text="Pet this record is for"
    )
    
    class Meta:
        model = MedicalRecord
        fields = [
            'pet', 'appointment_id', 'visit_date',
            'diagnosis', 'symptoms', 'treatment', 'prescription',
            'follow_up_required', 'follow_up_date',
            'notes', 'weight', 'temperature', 'test_results'
        ]
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        request = self.context.get('request')
        
        # Filter queryset based on user role
        if request and request.user.is_authenticated:
            user = request.user
            
            # Vets see appointments assigned to them
            if user.role == 'VETERINARIAN':
                self.fields['appointment_id'].queryset = Appointment.objects.filter(
                    veterinarian=user,
                    status='completed'
                )
                # Vets can only create records for pets in their appointments
                self.fields['pet'].queryset = PetProfile.objects.filter(
                    appointments__veterinarian=user
                ).distinct()
            
            # Clients can only see their own pets
            elif user.role == 'CLIENT':
                self.fields['pet'].queryset = PetProfile.objects.filter(owner=user)
    
    def validate_appointment_id(self, value):
        """Ensure appointment is completed"""
        if value and value.status != 'completed':
            raise serializers.ValidationError(
                "Medical records can only be created for completed appointments."
            )
        return value
    
    def validate_follow_up_date(self, value):
        """Ensure follow-up date is in the future"""
        if value and value <= timezone.now().date():
            raise serializers.ValidationError("Follow-up date must be in the future.")
        return value
    
    def validate(self, data):
        """Additional validation"""
        # Ensure follow-up date is provided if follow-up is required
        if data.get('follow_up_required') and not data.get('follow_up_date'):
            raise serializers.ValidationError({
                "follow_up_date": "Follow-up date is required when follow-up is needed."
            })
        
        # If appointment is provided, ensure pet matches
        appointment = data.get('appointment')
        pet = data.get('pet')
        if appointment and pet and appointment.pet != pet:
            raise serializers.ValidationError({
                "pet": "Pet must match the appointment's pet."
            })
        
        return data
    
    def create(self, validated_data):
        """Create medical record with the logged-in veterinarian"""
        request = self.context.get('request')
        
        # If appointment is provided and no pet specified, use appointment's pet
        if 'appointment' in validated_data and 'pet' not in validated_data:
            validated_data['pet'] = validated_data['appointment'].pet
        
        # Set veterinarian from request
        validated_data['veterinarian'] = request.user
        
        return super().create(validated_data)


class MedicalRecordUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = MedicalRecord
        fields = [
            'diagnosis', 'symptoms', 'treatment', 'prescription',
            'follow_up_required', 'follow_up_date',
            'notes', 'weight', 'temperature', 'test_results'
        ]
    
    def validate_follow_up_date(self, value):
        """Ensure follow-up date is in the future"""
        if value and value <= timezone.now().date():
            raise serializers.ValidationError("Follow-up date must be in the future.")
        return value
    
    def validate(self, data):
        """Ensure follow-up date is provided if follow-up is required"""
        follow_up_required = data.get('follow_up_required', self.instance.follow_up_required)
        follow_up_date = data.get('follow_up_date', self.instance.follow_up_date)
        
        if follow_up_required and not follow_up_date:
            raise serializers.ValidationError({
                "follow_up_date": "Follow-up date is required when follow-up is needed."
            })
        
        return data
