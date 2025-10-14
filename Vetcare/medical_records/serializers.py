from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import MedicalRecord
#from ..pets.serializers import PetSerializer #tells Python to go up one directory (from medical_records to the project root) and then into pets
from pets. serializers import PetSerializer
User = get_user_model()

class VetSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']


class MedicalRecordSerializer(serializers.ModelSerializer):
    pet = PetSerializer(read_only=True)
    pet_id = serializers.PrimaryKeyRelatedField(
        queryset=MedicalRecord._meta.get_field('pet').remote_field.model.objects.all(),
        source='pet',
        write_only=True
    )
    vet = VetSerializer(read_only=True)

    class Meta:
        model = MedicalRecord
        fields = [
            'id', 'pet', 'vet',
            'diagnosis', 'treatment', 'prescription',
            'visit_date', 'follow_up_date', 'notes'
        ]
        read_only_fields = ['id', 'vet', 'visit_date']

    def create(self, validated_data):
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['vet'] = request.user
        return super().create(validated_data)


class VaccinationSerializer(serializers.ModelSerializer):

    class Meta:
        model = MedicalRecord
        fields = [
            'id','pet', 'vet',
            'vaccine_name', 'date_administered', 'next_due_date', 'notes'
        ]
        read_only_fields = ['id', 'vet']

    def create(self, validated_data):
        """
        Automatically assign the logged-in vet as the one who administered the vaccine.
        """
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['vet'] = request.user
        return super().create(validated_data)