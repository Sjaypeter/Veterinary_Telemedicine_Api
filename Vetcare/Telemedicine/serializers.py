from rest_framework import serializers
from . models import OwnerProfile, PetProfile, Appointment, MedicalRecord, Vetprofile
from django.contrib.auth import authenticate, get_user_model
from rest_framework.authtoken.models import Token

class OwnerProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = OwnerProfile
        fields = ["__all__"]


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only= True,min_length=8)
    
    class Meta:
        model = OwnerProfile
        fields = ["__all__"]

    def create(self,validated_data):
        user = get_user_model().objects.create_user(
            username= validated_data['username'],
            email= validated_data['email'],
            password= validated_data['password']

        )
        Token.objects.create(user=user)
        return user
    
    #I have to change the owner profile form to abstrac user cause these fields arent in my models

class LoginSerializer(serializers.ModelSerializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only= True,min_length=8)

    def validate(self,data):
        user = authenticate(username=data['username'], password=data['password'])
        if not user:
            raise serializers.ValidationError("Invalid Credentials")
        data['user'] = user
        return data

