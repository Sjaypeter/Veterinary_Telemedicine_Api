from rest_framework import serializers
from django.utils import timezone

from .models import Appointment, Consultation
from accounts.models import Vetprofile, CustomUser
from pets.models import PetProfile


class AppointmentListSerializer(serializers.ModelSerializer):

    client_name = serializers.CharField(source='client.get_full_name', read_only=True)
    vet_name = serializers.CharField(source='veterinarian.get_full_name', read_only=True)
    pet_name = serializers.CharField(source='pet.name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = Appointment
        fields = [
            'id', 'client', 'client_name', 'veterinarian', 'vet_name',
            'pet', 'pet_name', 'date', 'time', 'status', 'status_display',
            'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class AppointmentDetailSerializer(serializers.ModelSerializer):
    client_email = serializers.EmailField(source='client.email', read_only=True)
    client_name = serializers.CharField(source='client.get_full_name', read_only=True)
    client_phone = serializers.CharField(source='client.phone', read_only=True)
    
    vet_email = serializers.EmailField(source='veterinarian.email', read_only=True)
    vet_name = serializers.CharField(source='veterinarian.get_full_name', read_only=True)
    vet_specialization = serializers.CharField(source='veterinarian.vet_profile.specialization', read_only=True)
    
    pet_name = serializers.CharField(source='pet.name', read_only=True)
    pet_species = serializers.CharField(source='pet.species', read_only=True)
    pet_breed = serializers.CharField(source='pet.breed', read_only=True)
    
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    has_consultation = serializers.SerializerMethodField()
    
    class Meta:
        model = Appointment
        fields = [
            'id', 'client', 'client_name', 'client_email', 'client_phone',
            'veterinarian', 'vet_name', 'vet_email', 'vet_specialization',
            'pet', 'pet_name', 'pet_species', 'pet_breed',
            'date', 'time', 'reason', 'status', 'status_display',
            'notes', 'has_consultation', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_has_consultation(self, obj):
        """Check if appointment has a consultation"""
        return hasattr(obj, 'consultation')


class AppointmentCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for clients to create new appointments.
    """
    veterinarian = serializers.PrimaryKeyRelatedField(
        queryset=Vetprofile.objects.filter(is_available=True),
        help_text="Select a veterinarian by their profile ID"
    )
    pet = serializers.PrimaryKeyRelatedField(
        queryset=PetProfile.objects.all(),
        help_text="Select one of your pets"
    )
    
    class Meta:
        model = Appointment
        fields = ['veterinarian', 'pet', 'date', 'reason', 'notes']
    
    def validate_pet(self, value):
        """Ensure the pet belongs to the requesting user"""
        request = self.context.get('request')
        if request and value.owner != request.user:
            raise serializers.ValidationError("You can only book appointments for your own pets.")
        return value
    
    def validate_date(self, value):
        """Ensure appointment date is not in the past"""
        if value < timezone.now().date():
            raise serializers.ValidationError("Appointment date cannot be in the past.")
        return value
    
    def validate_veterinarian(self, value):
        """Ensure the veterinarian is available"""
        if not value.is_available:
            raise serializers.ValidationError("This veterinarian is not currently available.")
        return value
    
    def create(self, validated_data):
        """Create appointment with the veterinarian user"""
        vet_profile = validated_data.pop('veterinarian')
        validated_data['veterinarian'] = vet_profile.user
        return super().create(validated_data)


class AppointmentUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating appointments.
    Veterinarians can update status, date, and time.
    """
    
    class Meta:
        model = Appointment
        fields = ['status', 'date', 'time', 'notes']
    
    def validate_status(self, value):
        """Validate status transitions"""
        instance = self.instance
        if not instance:
            return value
        
        current_status = instance.status
        
        # Define valid status transitions
        valid_transitions = {
            Appointment.PENDING: [Appointment.CONFIRMED, Appointment.CANCELLED],
            Appointment.CONFIRMED: [Appointment.COMPLETED, Appointment.CANCELLED],
            Appointment.COMPLETED: [],  # Cannot change from completed
            Appointment.CANCELLED: []   # Cannot change from cancelled
        }
        
        if value not in valid_transitions.get(current_status, []):
            raise serializers.ValidationError(
                f"Cannot change status from {current_status} to {value}."
            )
        
        return value
    
    def validate(self, data):
        """Additional validation for status-specific requirements"""
        status = data.get('status', self.instance.status if self.instance else None)
        
        # When confirming, require date and time
        if status == Appointment.CONFIRMED:
            if not data.get('date') and not self.instance.date:
                raise serializers.ValidationError({
                    "date": "Date is required when confirming appointment."
                })
            if not data.get('time') and not self.instance.time:
                raise serializers.ValidationError({
                    "time": "Time is required when confirming appointment."
                })
        
        return data


class AppointmentStatusUpdateSerializer(serializers.Serializer):
    """
    Simple serializer for status-only updates.
    """
    status = serializers.ChoiceField(choices=Appointment.STATUS_CHOICES)
    date = serializers.DateField(required=False)
    time = serializers.TimeField(required=False)
    
    def validate_status(self, value):
        """Ensure status is valid for the appointment"""
        instance = self.context.get('instance')
        if not instance:
            return value
        
        current_status = instance.status
        
        # Define valid status transitions
        valid_transitions = {
            Appointment.PENDING: [Appointment.CONFIRMED, Appointment.CANCELLED],
            Appointment.CONFIRMED: [Appointment.COMPLETED, Appointment.CANCELLED],
        }
        
        if value not in valid_transitions.get(current_status, []):
            raise serializers.ValidationError(
                f"Cannot change status from {current_status} to {value}."
            )
        
        return value


class ConsultationSerializer(serializers.ModelSerializer):
    """
    Serializer for creating and viewing consultations.
    """
    appointment_id = serializers.PrimaryKeyRelatedField(
        queryset=Appointment.objects.filter(status=Appointment.COMPLETED),
        source='appointment',
        write_only=True,
        help_text="ID of the completed appointment"
    )
    appointment_details = AppointmentDetailSerializer(source='appointment', read_only=True)
    vet_name = serializers.CharField(source='veterinarian.get_full_name', read_only=True)
    pet_name = serializers.CharField(source='pet.name', read_only=True)
    client_name = serializers.CharField(source='client.get_full_name', read_only=True)
    
    class Meta:
        model = Consultation
        fields = [
            'id', 'appointment_id', 'appointment_details',
            'veterinarian', 'vet_name', 'pet_name', 'client_name',
            'diagnosis', 'symptoms', 'notes', 'prescription',
            'follow_up_required', 'follow_up_date',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'veterinarian', 'created_at', 'updated_at']
    
    def validate_appointment_id(self, value):
        """Ensure appointment is completed and doesn't have a consultation"""
        if value.status != Appointment.COMPLETED:
            raise serializers.ValidationError(
                "Consultation can only be created for completed appointments."
            )
        
        if hasattr(value, 'consultation'):
            raise serializers.ValidationError(
                "A consultation already exists for this appointment."
            )
        
        # Ensure the vet creating the consultation is the assigned vet
        request = self.context.get('request')
        if request and value.veterinarian != request.user:
            raise serializers.ValidationError(
                "You can only create consultations for your own appointments."
            )
        
        return value
    
    def validate_follow_up_date(self, value):
        """Ensure follow-up date is in the future"""
        if value and value <= timezone.now().date():
            raise serializers.ValidationError("Follow-up date must be in the future.")
        return value
    
    def validate(self, data):
        """Ensure follow-up date is provided if follow-up is required"""
        if data.get('follow_up_required') and not data.get('follow_up_date'):
            raise serializers.ValidationError({
                "follow_up_date": "Follow-up date is required when follow-up is needed."
            })
        return data


class ConsultationListSerializer(serializers.ModelSerializer):
    
    vet_name = serializers.CharField(source='veterinarian.get_full_name', read_only=True)
    pet_name = serializers.CharField(source='pet.name', read_only=True)
    client_name = serializers.CharField(source='client.get_full_name', read_only=True)
    appointment_date = serializers.DateField(source='appointment.date', read_only=True)
    
    class Meta:
        model = Consultation
        fields = [
            'id', 'appointment', 'vet_name', 'pet_name', 'client_name',
            'appointment_date', 'diagnosis', 'follow_up_required',
            'follow_up_date', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']