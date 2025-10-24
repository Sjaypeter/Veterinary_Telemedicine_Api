from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import ClientProfile, Vetprofile, CustomUser


class CustomUserSerializer(serializers.ModelSerializer):
    """Serializer for CustomUser model - for reading user data"""
    
    full_name = serializers.SerializerMethodField()
    
    class Meta:
        model = CustomUser
        fields = [
            'id', 'email', 'first_name', 'last_name', 
            'full_name', 'role', 'phone', 'is_active',
            'created_at'
        ]
        read_only_fields = ['id', 'created_at']
    
    def get_full_name(self, obj):
        return obj.get_full_name()


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for user registration"""
    
    password = serializers.CharField(
        write_only=True, 
        min_length=8,
        style={'input_type': 'password'},
        help_text="Password must be at least 8 characters"
    )
    password_confirm = serializers.CharField(
        write_only=True,
        style={'input_type': 'password'},
        help_text="Confirm your password"
    )
    
    class Meta:
        model = CustomUser
        fields = [
            'email', 'password', 'password_confirm',
            'first_name', 'last_name', 'role', 'phone'
        ]
        extra_kwargs = {
            'first_name': {'required': True},
            'last_name': {'required': True},
            'email': {'required': True},
        }
    
    def validate_email(self, value):
        """Check if email is already registered"""
        if CustomUser.objects.filter(email=value.lower()).exists():
            raise serializers.ValidationError("This email is already registered.")
        return value.lower()
    
    def validate(self, data):
        """Validate that passwords match"""
        if data.get('password') != data.get('password_confirm'):
            raise serializers.ValidationError({
                "password_confirm": "Passwords do not match."
            })
        return data
    
    def create(self, validated_data):
        """Create user with hashed password"""
        # Remove password_confirm as it's not needed for user creation
        validated_data.pop('password_confirm')
        
        password = validated_data.pop('password')
        role = validated_data.get('role', CustomUser.CLIENT)
        
        # Create user
        user = CustomUser.objects.create_user(
            password=password,
            **validated_data
        )
        
        return user


class LoginSerializer(serializers.Serializer):
    """Serializer for user login"""
    
    email = serializers.EmailField()
    password = serializers.CharField(
        write_only=True,
        style={'input_type': 'password'}
    )
    
    def validate(self, data):
        """Authenticate user"""
        email = data.get('email', '').lower()
        password = data.get('password', '')
        
        if email and password:
            # Try to get the user
            try:
                user = CustomUser.objects.get(email=email)
            except CustomUser.DoesNotExist:
                raise serializers.ValidationError(
                    "Unable to log in with provided credentials."
                )
            
            # Check password
            if not user.check_password(password):
                raise serializers.ValidationError(
                    "Unable to log in with provided credentials."
                )
            
            # Check if user is active
            if not user.is_active:
                raise serializers.ValidationError(
                    "User account is disabled."
                )
            
            data['user'] = user
        else:
            raise serializers.ValidationError(
                "Must include 'email' and 'password'."
            )
        
        return data


class ClientProfileSerializer(serializers.ModelSerializer):
    """Serializer for Client Profile"""
    
    user = CustomUserSerializer(read_only=True)
    user_email = serializers.EmailField(source='user.email', read_only=True)
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    
    class Meta:
        model = ClientProfile
        fields = [
            'id', 'user', 'user_email', 'user_name',
            'address', 'emergency_contact',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']


class VetProfileSerializer(serializers.ModelSerializer):
    """Serializer for Veterinarian Profile"""
    
    user = CustomUserSerializer(read_only=True)
    user_email = serializers.EmailField(source='user.email', read_only=True)
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    
    class Meta:
        model = Vetprofile
        fields = [
            'id', 'user', 'user_email', 'user_name',
            'specialization', 'license_number', 
            'years_of_experience', 'bio', 'is_available',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']
    
    def validate_license_number(self, value):
        """Ensure license number is unique"""
        instance = self.instance
        if instance:
            # Updating existing profile
            if Vetprofile.objects.exclude(pk=instance.pk).filter(license_number=value).exists():
                raise serializers.ValidationError("This license number is already in use.")
        else:
            # Creating new profile
            if Vetprofile.objects.filter(license_number=value).exists():
                raise serializers.ValidationError("This license number is already in use.")
        return value


class VetProfileListSerializer(serializers.ModelSerializer):
    """Simplified serializer for listing veterinarians"""
    
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    user_email = serializers.EmailField(source='user.email', read_only=True)
    user_phone = serializers.CharField(source='user.phone', read_only=True)
    
    class Meta:
        model = Vetprofile
        fields = [
            'id', 'user_name', 'user_email', 'user_phone',
            'specialization', 'years_of_experience', 'is_available'
        ]


class UserProfileSerializer(serializers.ModelSerializer):
    """Complete user profile serializer (includes related profile)"""
    
    client_profile = ClientProfileSerializer(read_only=True)
    vet_profile = VetProfileSerializer(read_only=True)
    
    class Meta:
        model = CustomUser
        fields = [
            'id', 'email', 'first_name', 'last_name', 
            'role', 'phone', 'is_active',
            'client_profile', 'vet_profile',
            'created_at'
        ]
        read_only_fields = ['id', 'email', 'role', 'created_at']