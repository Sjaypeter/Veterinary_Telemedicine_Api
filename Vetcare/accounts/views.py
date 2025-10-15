from django.shortcuts import render, redirect
from . serializers import CustomUserSerializer, OwnerProfileSerializer, VetProfileSerializer,RegisterSerializer,LoginSerializer
from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.authtoken.views import ObtainAuthToken
from django.contrib.auth import get_user_model, authenticate
from . models import CustomUser, Vetprofile,OwnerProfile
from django.shortcuts import get_object_or_404


# Create your views here.


User = get_user_model()


class RegisterView(generics.CreateAPIView):
    """Allows a new user to register (vet or owner)."""

    queryset = CustomUser.objects.all()
    serializer_class = RegisterSerializer


    def perform_create(self, serializer):
        user = serializer.save()
        # Automatically create a profile based on user type
        if user.is_owner:
            OwnerProfile.objects.create(user=user)
        elif user.is_vet:
            Vetprofile.objects.create(user=user)
        return user
    



class LoginView(APIView):
    """Handles user authentication and login (for both vets and clients)."""
    permission_classes = [AllowAny]

    def get(self, request):
        """Display the login form in the browsable API."""
        serializer = LoginSerializer()
        return Response(serializer.data)

    def post(self, request):
        """Authenticate and log in a user."""
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data.get("email")
        password = serializer.validated_data.get("password")

        user = authenticate(request, email=email, password=password)
        if not user:
            return Response(
                {"detail": "Invalid credentials."},
                status=status.HTTP_401_UNAUTHORIZED
            )

        return Response({
            "message": "Login successful",
            "user": CustomUserSerializer(user).data
        }, status=status.HTTP_200_OK)


class UserProfileView(generics.RetrieveUpdateAPIView):
    """Allows users to view or update their own profile."""
    serializer_class = CustomUserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

class UserListView(generics.ListAPIView):
    """List all users — can be filtered or searched later."""
    queryset = User.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = [IsAuthenticated]

    