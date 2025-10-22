# pets/serializers.py
from rest_framework import serializers
from django.utils import timezone

from .models import PetProfile
from accounts.models import CustomUser


class PetProfileListSerializer(serializers.ModelSerializer):

    owner_name = serializers.CharField(source='owner.get_full_name', read_only=True)
    owner_email = serializers.EmailField(source='owner.email', read_only=True)
    calculated_age = serializers.CharField(read_only=True)
    
    class Meta:
        model = PetProfile
        fields = [
            'id', 'owner', 'owner_name', 'owner_email',
            'name', 'species', 'breed', 'gender',
            'age', 'calculated_age', 'weight',
            'profile_image', 'is_active', 'created_at'
        ]
        read_only_fields = ['id', 'owner', 'created_at']


class PetProfileDetailSerializer(serializers.ModelSerializer):
    
    owner_name = serializers.CharField(source='owner.get_full_name', read_only=True)
    owner_email = serializers.EmailField(source='owner.email', read_only=True)
    owner_phone = serializers.CharField(source='owner.phone', read_only=True)
    calculated_age = serializers.CharField(read_only=True)
    has_medical_conditions = serializers.BooleanField(read_only=True)
    needs_attention = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = PetProfile
        fields = [
            'id', 'owner', 'owner_name', 'owner_email', 'owner_phone',
            'name', 'species', 'breed', 'gender', 'color',
            'date_of_birth', 'age', 'calculated_age',
            'weight', 'microchip_number',
            'allergies', 'medical_conditions', 'current_medications',
            'profile_image', 'notes', 'is_active',
            'has_medical_conditions', 'needs_attention',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'owner', 'created_at', 'updated_at']


class PetProfileCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating pet profiles (Client only).
    """
    
    class Meta:
        model = PetProfile
        fields = [
            'name', 'species', 'breed', 'gender', 'color',
            'date_of_birth', 'age', 'weight', 'microchip_number',
            'allergies', 'medical_conditions', 'current_medications',
            'profile_image', 'notes'
        ]
    
    def validate(self, data):
        """Ensure either date_of_birth or age is provided"""
        if not data.get('date_of_birth') and not data.get('age'):
            raise serializers.ValidationError(
                "Either date of birth or age must be provided."
            )
        return data
    
    def validate_date_of_birth(self, value):
        """Ensure date of birth is not in the future"""
        if value and value > timezone.now().date():
            raise serializers.ValidationError("Date of birth cannot be in the future.")
        return value
    
    def validate_microchip_number(self, value):
        """Ensure microchip number is unique"""
        if value and PetProfile.objects.filter(microchip_number=value).exists():
            raise serializers.ValidationError("This microchip number is already registered.")
        return value


class PetProfileUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating pet profiles (Owner only).
    """
    
    class Meta:
        model = PetProfile
        fields = [
            'name', 'species', 'breed', 'gender', 'color',
            'date_of_birth', 'age', 'weight', 'microchip_number',
            'allergies', 'medical_conditions', 'current_medications',
            'profile_image', 'notes', 'is_active'
        ]
    
    def validate_date_of_birth(self, value):
        """Ensure date of birth is not in the future"""
        if value and value > timezone.now().date():
            raise serializers.ValidationError("Date of birth cannot be in the future.")
        return value
    
    def validate_microchip_number(self, value):
        """Ensure microchip number is unique (excluding current instance)"""
        if value:
            instance = self.instance
            existing = PetProfile.objects.filter(microchip_number=value)
            if instance:
                existing = existing.exclude(pk=instance.pk)
            if existing.exists():
                raise serializers.ValidationError("This microchip number is already registered.")
        return value


class MyPetsSerializer(serializers.ModelSerializer):
   
    calculated_age = serializers.CharField(read_only=True)
    needs_attention = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = PetProfile
        fields = [
            'id', 'name', 'species', 'breed', 'gender',
            'age', 'calculated_age', 'weight',
            'allergies', 'medical_conditions', 'current_medications',
            'needs_attention', 'profile_image', 'is_active'
        ]
        read_only_fields = ['id']