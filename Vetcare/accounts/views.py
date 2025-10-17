from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth import get_user_model

from .serializers import (
    UserRegistrationSerializer,
    LoginSerializer,
    CustomUserSerializer,
    ClientProfileSerializer,
    VetProfileSerializer,
    VetProfileListSerializer,
    UserProfileSerializer
)
from .models import CustomUser, Vetprofile, ClientProfile
from .permissions import IsVeterinarian, IsClient


# AUTHENTICATION VIEWS 

class UserRegistrationView(generics.CreateAPIView):
    """
    Register a new user (Veterinarian or Client)
    """
    queryset = CustomUser.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        
        return Response({
            "user": CustomUserSerializer(user).data,
            "tokens": {
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            },
            "message": "User registered successfully"
        }, status=status.HTTP_201_CREATED)


class UserLoginView(generics.GenericAPIView):
    """
    Login user and return JWT tokens.
    """
    serializer_class = LoginSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        
        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        
        return Response({
            "user": CustomUserSerializer(user).data,
            "tokens": {
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            },
            "message": "Login successful"
        }, status=status.HTTP_200_OK)


class UserLogoutView(APIView):
    """
    Logout user by blacklisting the refresh token.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get("refresh")
            if not refresh_token:
                return Response(
                    {"error": "Refresh token is required"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            token = RefreshToken(refresh_token)
            token.blacklist()
            
            return Response(
                {"message": "Logout successful"},
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {"error": "Invalid token"},
                status=status.HTTP_400_BAD_REQUEST
            )


class CurrentUserView(generics.RetrieveAPIView):
    """
    Get current authenticated user with profile.
    """
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user


# CLIENT PROFILE VIEWS 

class ClientProfileListView(generics.ListAPIView):
    """
    List all client profiles (for vets to view).
    """
    queryset = ClientProfile.objects.select_related('user').all()
    serializer_class = ClientProfileSerializer
    permission_classes = [IsAuthenticated, IsVeterinarian]


class ClientProfileDetailView(generics.RetrieveUpdateAPIView):
    """
    View or update own client profile.
    """
    serializer_class = ClientProfileSerializer
    permission_classes = [IsAuthenticated, IsClient]

    def get_queryset(self):
        # Clients can only access their own profile
        return ClientProfile.objects.filter(user=self.request.user)
    
    def get_object(self):
        """Get the client profile for the current user"""
        queryset = self.get_queryset()
        obj = queryset.first()
        
        if not obj:
            # Create profile if it doesn't exist
            obj = ClientProfile.objects.create(user=self.request.user)
        
        return obj


class MyClientProfileView(generics.RetrieveUpdateAPIView):
    """
    Convenient endpoint for current user's client profile.
    """
    serializer_class = ClientProfileSerializer
    permission_classes = [IsAuthenticated, IsClient]

    def get_object(self):
        obj, created = ClientProfile.objects.get_or_create(user=self.request.user)
        return obj


#  VET PROFILE VIEWS 

class VetProfileListView(generics.ListAPIView):
    """
    List all veterinarian profiles (public view for clients).
    """
    queryset = Vetprofile.objects.select_related('user').filter(
        is_available=True
    )
    serializer_class = VetProfileListSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by specialization if provided
        specialization = self.request.query_params.get('specialization')
        if specialization:
            queryset = queryset.filter(specialization__icontains=specialization)
        
        # Filter by availability if provided
        is_available = self.request.query_params.get('is_available')
        if is_available is not None:
            is_available = is_available.lower() == 'true'
            queryset = queryset.filter(is_available=is_available)
        
        return queryset.order_by('user__first_name')


class VetProfileDetailView(generics.RetrieveAPIView):
    """
    View a specific veterinarian profile (public view).
    """
    queryset = Vetprofile.objects.select_related('user').all()
    serializer_class = VetProfileSerializer
    permission_classes = [IsAuthenticated]


class MyVetProfileView(generics.RetrieveUpdateAPIView):
    """
    View or update own vet profile.
    """
    serializer_class = VetProfileSerializer
    permission_classes = [IsAuthenticated, IsVeterinarian]

    def get_object(self):
        obj, created = Vetprofile.objects.get_or_create(user=self.request.user)
        return obj


class VetProfileUpdateView(generics.UpdateAPIView):
    """
    Update specific vet profile (own profile only).
    """
    serializer_class = VetProfileSerializer
    permission_classes = [IsAuthenticated, IsVeterinarian]

    def get_queryset(self):
        # Vets can only update their own profile
        return Vetprofile.objects.filter(user=self.request.user)


# USER MANAGEMENT VIEWS 

class UserListView(generics.ListAPIView):
    """
    List all users (admin only).
    """
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Only show users if requester is staff/superuser
        if self.request.user.is_staff:
            return CustomUser.objects.all().order_by('-created_at')
        # Regular users can only see themselves
        return CustomUser.objects.filter(id=self.request.user.id)


class UserDetailView(generics.RetrieveUpdateAPIView):
    """
    View or update user details.
    """
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Users can only access their own details unless staff
        if self.request.user.is_staff:
            return CustomUser.objects.all()
        return CustomUser.objects.filter(id=self.request.user.id)