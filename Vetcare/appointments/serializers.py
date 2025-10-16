from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Appointment, Consultation
from accounts . models import Vetprofile
from pets.models import PetProfile


User = get_user_model()

class AppointmentSerializer(serializers.ModelSerializer):
    veterinarian = serializers.StringRelatedField(read_only=True)
    client = serializers.StringRelatedField(read_only=True)



    class Meta:
        model = Appointment
        fields = [
            'id', 'client', 'veterinarian', 'pet', 'pet_id',
            'appointment_date', 'reason', 'status',
        ]
        read_only_fields = ['veterinarian', 'client', 'status', 'reason']


    def __init__(self, *args, **kwargs):
        #Customizes fields dynamically based on user role
        super().__init__(*args, **kwargs)
        request = self.context.get('request')    

        if request:
            if request.user.role == 'client':
                self.fields['status'].read_only = True

            elif request.user.role == 'veterinarian':
                self.fields['reason'].read_only = True


#For creating appointments
class Appointmentcreateserializer(serializers.ModelSerializer):
    veterinarian = serializers.PrimaryKeyRelatedField(queryset=Vetprofile.objects.all())

    class Meta:
        model = Appointment
        fields = ['veterinarian', 'reason']




class ConsultationSerializer(serializers.ModelSerializer):
    appointment_id = serializers.PrimaryKeyRelatedField(
        queryset=Appointment.objects.all(), source='appointment', write_only=True
    )
    appointment = AppointmentSerializer(read_only=True)

    class Meta:
        model = Consultation
        fields = [
            'id','owner', 'appointment', 'appointment_id',
            'notes', 'prescription', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']

    def validate(self, data):
        appointment = data.get('appointment')
        if hasattr(appointment, 'consultation'):
            raise serializers.ValidationError("A consultation already exists for this appointment.")
        return data

#Prevents multiple consultations for the same appointment.

#Allows creation using an appointment_id field.


