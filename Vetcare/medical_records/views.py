
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import MedicalRecord, Vaccination
from appointments.models import Appointment
from medical_records.serializers import MedicalRecordSerializer, VaccinationSerializer
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
    serializer_class = MedicalRecord
    permission_classes = [IsVeterinarian]

    def perform_create(self, serializer):
        #Ensure vets can only make records for their own appointments
        appointment_id = self.request.data.get('appointment')
        appointment = get_object_or_404(Appointment, id=appointment_id)

        if appointment.veterinarian != self.request.user:
            raise PermissionDenied("You can only create records for your own appointments.")

        serializer.save(appointment=appointment)


class VaccinationListCreateView(generics.ListCreateAPIView):
    
    #GET: List vaccination history for a pet or all pets of the owner.- POST: Vets can record a new vaccination.

    serializer_class = VaccinationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if getattr(user, "is_vet", False):
            return Vaccination.objects.filter(vet=user).order_by("-date_administered")
        return Vaccination.objects.filter(pet__owner=user).order_by("-date_administered")

    def perform_create(self, serializer):
        user = self.request.user
        if not getattr(user, "is_vet", False):
            raise PermissionDenied("Only veterinarians can record vaccinations.")
        
        pet_id = self.request.data.get("pet")
        pet = get_object_or_404(PetProfile, id=pet_id)

        serializer.save(vet=user, pet=pet)

class VaccinationDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve or update vaccination details.
    - Vets can edit.
    - Owners can view.
    """
    serializer_class = VaccinationSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = Vaccination.objects.all()

    def get_object(self):
        record = get_object_or_404(Vaccination, pk=self.kwargs["pk"])
        user = self.request.user

        if record.vet != user and record.pet.owner != user:
            self.permission_denied(self.request, message="You are not authorized to access this record.")
        return record

    def update(self, request, *args, **kwargs):
        record = self.get_object()
        if record.vet != request.user:
            return Response({"error": "Only the vet who recorded this vaccination can update it."}, status=status.HTTP_403_FORBIDDEN)
        return super().update(request, *args, **kwargs)



