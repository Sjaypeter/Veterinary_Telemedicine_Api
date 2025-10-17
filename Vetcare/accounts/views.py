from django.shortcuts import render, redirect
from . serializers import CustomUserSerializer, ClientProfileSerializer, VetProfileSerializer
from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import authenticate, login,logout
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.authtoken.views import ObtainAuthToken
from django.contrib.auth import get_user_model, authenticate
from . models import CustomUser, Vetprofile,ClientProfile


# Create your views here.


User = get_user_model()


class RegisterView(generics.CreateAPIView):
    """Registers a new Vet or Client."""
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = [permissions.AllowAny]






#----------CLIENT PROFILE
class ClientprofileView(generics.ListAPIView):
    """Allows users to view or update their own profile."""
    queryset = ClientProfile.objects.all()
    serializer_class = ClientProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    

class ClientprofiledetailView(generics.RetrieveUpdateAPIView):
    serializer_class = ClientProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        #Only clients allowed to alter this
        user = self.request.user
        if user.role == 'client':
            return ClientProfile.objects.filter(user=user)
        return ClientProfile.objects.none()
    



#----------VET PROFILE

class Vetprofileview(generics.ListAPIView):
    queryset = Vetprofile.objects.all()
    serializer_class = VetProfileSerializer
    permission_classes = [permissions.IsAuthenticated]


class VetprofiledetailView(generics.RetrieveUpdateAPIView):
    serializer_class = VetProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        #Only vets allowed to alter this
        user = self.request.user
        if user.role == 'veterinarian':
            return Vetprofile.objects.filter(user=user)
        return Vetprofile.objects.none()

    