from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate
from .models import OwnerProfile, Vetprofile

User = get_user_model()


class CustomUserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'bio', 'profile_picture', 'is_vet', 'is_owner'
        ]


class RegisterSerializer(serializers.ModelSerializer):
    #Allows setting user type (vet/owner) at registration.
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'is_vet', 'is_owner']

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email'),
            password=validated_data['password'],
            is_vet=validated_data.get('is_vet', False),
            is_owner=validated_data.get('is_owner', False),
        )
        return user



class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        user = authenticate(username=data['username'], password=data['password'])
        if user and user.is_active:
            return user
        raise serializers.ValidationError("Invalid credentials or inactive account.")


class OwnerProfileSerializer(serializers.ModelSerializer):
    user = CustomUserSerializer(read_only=True)

    class Meta:
        model = OwnerProfile
        fields = ['id', 'user', 'phone', 'address']

class VetProfileSerializer(serializers.ModelSerializer):
    user = CustomUserSerializer(read_only=True)

    class Meta:
        model = Vetprofile
        fields = ['id', 'user', 'specialization', 'license_number']
