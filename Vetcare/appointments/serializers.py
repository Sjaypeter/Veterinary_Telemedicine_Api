from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Appointment, Consultation
from pets.models import PetProfile


User = get_user_model()

class AppointmentSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.username')
    vet_name = serializers.ReadOnlyField(source='vet.username')
    pet_id = serializers.PrimaryKeyRelatedField(queryset=PetProfile.objects.all(), source='pet', write_only=True)

    class Meta:
        model = Appointment
        fields = [
            'id', 'owner', 'vet', 'vet_name', 'pet', 'pet_id',
            'date', 'reason', 'status', 'created_at'
        ]
        read_only_fields = ['id', 'owner', 'created_at', 'status']

    def create(self, validated_data):
        validated_data['owner'] = self.context['request'].user
        return super().create(validated_data)
    
#Shows owner username and vet username (read-only).

#Allows setting the pet via pet_id for clean API requests.

#Automatically assigns the logged-in user as the owner when creating an appointment.




class ConsultationSerializer(serializers.ModelSerializer):
    appointment_id = serializers.PrimaryKeyRelatedField(
        queryset=Appointment.objects.all(), source='appointment', write_only=True
    )
    appointment = AppointmentSerializer(read_only=True)

    class Meta:
        model = Consultation
        fields = [
            'id', 'appointment', 'appointment_id',
            'notes', 'diagnosis', 'prescription', 'follow_up_date', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']

    def validate(self, data):
        appointment = data.get('appointment')
        if hasattr(appointment, 'consultation'):
            raise serializers.ValidationError("A consultation already exists for this appointment.")
        return data

#Prevents multiple consultations for the same appointment.

#Allows creation using an appointment_id field.


