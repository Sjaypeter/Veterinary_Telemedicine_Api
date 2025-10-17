from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import MedicalRecord
from appointments.models import Appointment



class MedicalRecordSerializer(serializers.ModelSerializer):
    appointment = serializers.PrimaryKeyRelatedField(
        queryset=Appointment.objects.none(),  # default empty until set in __init__
        write_only=True
    )
    veterinarian = serializers.CharField(source='appointment.veterinarian.username', read_only=True)
    client = serializers.CharField(source='appointment.client.username', read_only=True)

    class Meta:
        model = MedicalRecord
        fields = "__all__"
        read_only_fields = ['id', 'veterinarian','pet', 'visit_date']

    def create(self, validated_data):
        request = self.context.get('request')
        appointment = validated_data.pop('appointment')
        # Automatically assign the pet from the appointment
        validated_data['pet'] = appointment.pet
        return MedicalRecord.objects.create(**validated_data)
    


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        request = self.context.get('request', None)

        if request and hasattr(request, 'user'):
            user = request.user

            # If veterinarian: show only their appointments
            if hasattr(user, 'vetprofile'):
                self.fields['appointment'].queryset = Appointment.objects.filter(veterinarian=user)

            # If client: show only their appointments
            elif hasattr(user, 'clientprofile'):
                self.fields['appointment'].queryset = Appointment.objects.filter(client=user)

            # Otherwise allow all (optional)
            else:
                self.fields['appointment'].queryset = Appointment.objects.all()



