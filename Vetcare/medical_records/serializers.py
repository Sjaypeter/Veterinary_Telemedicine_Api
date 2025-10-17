from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import MedicalRecord
from appointments . models import Appointment


User = get_user_model()

class MedicalRecordSerializer(serializers.ModelSerializer):
    appointment = serializers.PrimaryKeyRelatedField(
        queryset=Appointment.objects.none(),  # default empty until set in __init__
        write_only=True
    )
    veterinarian = serializers.CharField(source='appointment.veterinarian.username', read_only=True)
    client = serializers.CharField(source='appointment.client.username', read_only=True)

    class Meta:
        model = MedicalRecord
        fields = [
            'pet_id', 'pet', 'vet',
            'diagnosis', 'treatment', 'prescription',
            'visit_date', 'follow_up_date', 'notes'
        ]
        read_only_fields = ['id', 'veterinarian','pet', 'visit_date']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        request = self.context.get('request')
        if request and hasattr(request, 'user') and request.user.is_authenticated:
            # If the logged-in user is a vet, show only their appointments
            if request.user.role == 'veterinarian':
                self.fields['appointment'].queryset = Appointment.objects.filter(veterinaraian=request.user)


