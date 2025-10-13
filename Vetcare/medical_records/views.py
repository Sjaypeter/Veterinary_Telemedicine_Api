
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import MedicalRecord, Vaccination
from medical_records. serializers import MedicalRecordSerializer, VaccinationSerializer
from django.utils import timezone
from pets.models import PetProfile
from rest_framework.exceptions import PermissionDenied


class MedicalRecordListCreateView(generics.ListCreateAPIView):
    
    #GET: List all medical records for the authenticated user’s pets. POST: Vets can create new medical records for a pet.
    
    serializer_class = MedicalRecordSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        # Owners see their own pets' records; vets see records they created
        if getattr(user, "is_vet", False):
            return MedicalRecord.objects.filter(vet=user).order_by("-record_date")
        return MedicalRecord.objects.filter(pet__owner=user).order_by("-record_date")

    def perform_create(self, serializer):
        user = self.request.user

        if not getattr(user, "is_vet", False):
            raise PermissionDenied("Only veterinarians can create medical records.")
        
        pet_id = self.request.data.get("pet")
        pet = get_object_or_404(PetProfile, id=pet_id)

        serializer.save(vet=user, pet=pet)



class MedicalRecordDetailView(generics.RetrieveUpdateDestroyAPIView):
    
    #View or edit a single medical record.- Only the vet who created it can edit/delete. - The owner of the pet can view it.


    serializer_class = MedicalRecordSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = MedicalRecord.objects.all()

    def get_object(self):
        record = get_object_or_404(MedicalRecord, pk=self.kwargs["pk"])
        user = self.request.user

        if record.vet != user and record.pet.owner != user:
            self.permission_denied(self.request, message="You are not authorized to access this record.")
        return record

    def update(self, request, *args, **kwargs):
        record = self.get_object()
        if record.vet != request.user:
            return Response({"error": "Only the vet who created this record can update it."}, status=status.HTTP_403_FORBIDDEN)
        return super().update(request, *args, **kwargs)


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



