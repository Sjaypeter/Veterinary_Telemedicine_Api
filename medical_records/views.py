from rest_framework import generics, permissions
from rest_framework.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404

from .models import MedicalRecord
from .serializers import (MedicalRecordListSerializer,MedicalRecordDetailSerializer,MedicalRecordCreateSerializer,MedicalRecordUpdateSerializer)
from .permissions import (IsMedicalRecordParticipant,CanCreateMedicalRecord,CanAccessPetMedicalHistory)
from accounts.permissions import IsVeterinarian


#MEDICAL RECORD VIEWS 

class MedicalRecordListView(generics.ListAPIView):
    """
    - Veterinarians see records they created
    - Clients see records for their pets
    """
    serializer_class = MedicalRecordListSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Return medical records based on user role"""
        user = self.request.user
        
        if user.role == 'VETERINARIAN':
            return MedicalRecord.objects.filter(
                veterinarian=user
            ).select_related('pet', 'veterinarian', 'appointment').order_by('-visit_date')
        
        elif user.role == 'CLIENT':
            return MedicalRecord.objects.filter(
                pet__owner=user
            ).select_related('pet', 'veterinarian', 'appointment').order_by('-visit_date')
        
        return MedicalRecord.objects.none()


class MedicalRecordDetailView(generics.RetrieveUpdateAPIView):
    """
    View or update a specific medical record.
    """
    queryset = MedicalRecord.objects.select_related('pet', 'veterinarian', 'appointment').all()
    permission_classes = [permissions.IsAuthenticated, IsMedicalRecordParticipant]

    def get_serializer_class(self):
        """Use different serializers for read vs write"""
        if self.request.method in ['PUT', 'PATCH']:
            return MedicalRecordUpdateSerializer
        return MedicalRecordDetailSerializer


class MedicalRecordCreateView(generics.CreateAPIView):
    """
    Create a medical record (Veterinarians only).
    """
    serializer_class = MedicalRecordCreateSerializer
    permission_classes = [permissions.IsAuthenticated, CanCreateMedicalRecord]

    def perform_create(self, serializer):
        """Save record with the logged-in veterinarian"""
        serializer.save(veterinarian=self.request.user)


class PetMedicalHistoryView(generics.ListAPIView):
    """
    View complete medical history for a specific pet.
    """
    serializer_class = MedicalRecordListSerializer
    permission_classes = [permissions.IsAuthenticated, CanAccessPetMedicalHistory]

    def get_queryset(self):
        """Return all medical records for the specified pet"""
        pet_id = self.kwargs.get('pet_id')
        return MedicalRecord.objects.filter(
            pet_id=pet_id
        ).select_related('veterinarian', 'appointment').order_by('-visit_date')


class MyPetsMedicalRecordsView(generics.ListAPIView):
    """
    View all medical records for all pets owned by the client.
    """
    serializer_class = MedicalRecordListSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Return records for all pets owned by the client"""
        user = self.request.user
        
        if user.role != 'CLIENT':
            return MedicalRecord.objects.none()
        
        return MedicalRecord.objects.filter(
            pet__owner=user
        ).select_related('pet', 'veterinarian', 'appointment').order_by('-visit_date')


class RecentMedicalRecordsView(generics.ListAPIView):
    """
    View recent medical records (last 30 days).
    """
    serializer_class = MedicalRecordListSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Return recent medical records based on user role"""
        from datetime import timedelta
        from django.utils import timezone
        
        user = self.request.user
        thirty_days_ago = timezone.now() - timedelta(days=30)
        
        base_query = MedicalRecord.objects.filter(
            visit_date__gte=thirty_days_ago
        ).select_related('pet', 'veterinarian', 'appointment')
        
        if user.role == 'VETERINARIAN':
            return base_query.filter(veterinarian=user).order_by('-visit_date')
        
        elif user.role == 'CLIENT':
            return base_query.filter(pet__owner=user).order_by('-visit_date')
        
        return MedicalRecord.objects.none()


class FollowUpRequiredView(generics.ListAPIView):
    """
    List medical records that require follow-up.
    """
    serializer_class = MedicalRecordListSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Return records with pending follow-ups"""
        from django.utils import timezone
        
        user = self.request.user
        today = timezone.now().date()
        
        base_query = MedicalRecord.objects.filter(
            follow_up_required=True,
            follow_up_date__gte=today
        ).select_related('pet', 'veterinarian', 'appointment')
        
        if user.role == 'VETERINARIAN':
            return base_query.filter(veterinarian=user).order_by('follow_up_date')
        
        elif user.role == 'CLIENT':
            return base_query.filter(pet__owner=user).order_by('follow_up_date')
        
        return MedicalRecord.objects.none()