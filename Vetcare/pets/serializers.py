from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import PetProfile

User = get_user_model()


class PetSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.username')

    class Meta:
        model = PetProfile
        fields = [
            'id', 'owner', 'name', 'species',
            'breed', 'age', 'gender', 'weight',
            'profile_image', 'created_at'
        ]
        read_only_fields = ['id', 'owner', 'created_at']

    def create(self, validated_data):
        validated_data['owner'] = self.context['request'].user
        return super().create(validated_data)
    

    #Automatically assigns the logged-in user as the owner when a petprofile is created.
