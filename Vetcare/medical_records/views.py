
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import MedicalRecord
from appointments.models import Appointment
from medical_records.serializers import MedicalRecordSerializer
from django.utils import timezone
from pets.models import PetProfile
from rest_framework.exceptions import PermissionDenied
from accounts.permissions import IsClient, IsVeterinarian


class MedicalRecordListView(generics.ListAPIView):
    
    #GET: List all medical records for the authenticated user’s pets.
    

    serializer_class = MedicalRecordSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'veterinarian':
            return MedicalRecord.objects.filter(appointment__veterinarian=user)
        elif user.role == 'patient':
            return MedicalRecord.objects.filter(appointment__client=user)
        return MedicalRecord.objects.none()



class MedicalRecordCreateView(generics.CreateAPIView):
    #Only vetss can create medical records
    serializer_class = MedicalRecordSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        #Ensure vets can only make records for their own appointments
        appointment_id = self.request.data.get('appointment')
        appointment = get_object_or_404(Appointment, id=appointment_id)

        if appointment.veterinarian != self.request.user:
            raise PermissionDenied("You can only create records for your own appointments.")

        serializer.save(appointment=appointment)

