from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import OwnerProfile, Vetprofile, PetProfile, Appointment, MedicalRecord
from .serializers import OwnerProfileSerializer, VetprofileSerializer, PetProfileSerializer, AppointmentSerializer, MedicalRecordSerializer
# Create your views here.

class OwnerProfileView(viewsets.ModelViewSet):
    queryset = OwnerProfile.objects.all()
    serializer_class = OwnerProfileSerializer
    permission_classes = [IsAuthenticated]
    

class VetprofileViewset(viewsets.ModelViewSet):
    queryset = Vetprofile.objects.all()
    serializer_class = VetprofileSerializer
    permission_classes = [IsAuthenticated]
    

class PetProfileViewset(viewsets.ModelViewSet):
    queryset = PetProfile.objects.all()
    serializer_class = VetprofileSerializer
    permission_classes = [IsAuthenticated]

    
class AppointmentViewset(viewsets.ModelViewSet):
    queryset = Appointment.objects.all()
    serializer_class = AppointmentSerializer
    permission_classes = [IsAuthenticated]


class MedicalRecordView(viewsets.ModelViewSet):
    queryset = MedicalRecord.objects.all()
    serializer_class= MedicalRecordSerializer
    permission_classes = [IsAuthenticated]
    
    
    