from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate
from .models import OwnerProfile, Vetprofile
from .models import CustomUser

User = get_user_model()


class CustomUserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'role', 'password'
        ]

    def create(self, validated_data):
        """Create user with hashed password and auto profile based on role"""
        password = validated_data.pop('password', None)
        role = validated_data.pop('role', None)

        user = User(**validated_data)
        if password:
            user.set_password(password)

        if role:
            user.role = role

        #Automatically create related profile
        if role == 'veterinarian':
            Vetprofile.objects.create(user=user)

        elif role == 'client':
            OwnerProfile.objects.create(user=user)

        return user


#class RegisterSerializer(serializers.ModelSerializer):
 #   #Allows setting user type (vet/owner) at registration.
  #  password = serializers.CharField(write_only=True)

   # class Meta:
    #    model = User
     #   fields = ['username', 'email', 'password', 'is_vet', 'is_owner']

#    def create(self, validated_data):
 #          username=validated_data['username'],
  #          email=validated_data.get('email'),
   #         password=validated_data['password'],
    #        is_vet=validated_data.get('is_vet', False),
     #       is_owner=validated_data.get('is_owner', False),
      #  )
       # return user



#class LoginSerializer(serializers.Serializer):
 #   email = serializers.EmailField()
  #  password = serializers.CharField(write_only=True)

   # def validate(self, data):
    #    email = data.get("email")
     #   password = data.get("password")

      #  if not email or not password:
       #     raise serializers.ValidationError("Both email and password are required.")

        #user = authenticate(email=email, password=password)
        #if not user:
         #   raise serializers.ValidationError("Invalid login credentials.")

        #data["user"] = user
        #return data


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
