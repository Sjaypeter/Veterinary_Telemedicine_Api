from rest_framework import generics, permissions, status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from .models import PetProfile
from .serializers import (PetProfileListSerializer,PetProfileDetailSerializer,PetProfileCreateSerializer,PetProfileUpdateSerializer,MyPetsSerializer,)
from .permissions import ( IsPetOwner, IsPetOwnerOrReadOnlyForVet, CanCreatePet, CanAccessPetList
)
from accounts.permissions import IsClient, IsVeterinarian


# PET PROFILE VIEWS 

class PetListView(generics.ListAPIView):
    """
    List pets based on user role.
    - Clients see their own pets
    - Veterinarians see pets they've treated
    """
    serializer_class = PetProfileListSerializer
    permission_classes = [permissions.IsAuthenticated, CanAccessPetList]

    def get_queryset(self):
        """Return pets based on user role"""
        user = self.request.user
        
        if user.role == 'CLIENT':
            # Clients see only their own pets
            return PetProfile.objects.filter(
                owner=user
            ).select_related('owner').order_by('-created_at')
        
        elif user.role == 'VETERINARIAN':
            # Veterinarians see pets they've treated
            from appointments.models import Appointment
            treated_pet_ids = Appointment.objects.filter(
                veterinarian=user
            ).values_list('pet_id', flat=True).distinct()
            
            return PetProfile.objects.filter(
                id__in=treated_pet_ids
            ).select_related('owner').order_by('-created_at')
        
        return PetProfile.objects.none()


class PetDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    View, update, or delete a specific pet.
    """
    queryset = PetProfile.objects.select_related('owner').all()
    permission_classes = [permissions.IsAuthenticated, IsPetOwnerOrReadOnlyForVet]

    def get_serializer_class(self):
        """Use different serializers for read vs write"""
        if self.request.method in ['PUT', 'PATCH']:
            return PetProfileUpdateSerializer
        return PetProfileDetailSerializer
    
    def perform_destroy(self, instance):
        """Soft delete by marking as inactive instead of hard delete"""
        instance.is_active = False
        instance.save()


class PetCreateView(generics.CreateAPIView):
    """
    Create a new pet profile (Client only).
    """
    serializer_class = PetProfileCreateSerializer
    permission_classes = [permissions.IsAuthenticated, CanCreatePet]

    def perform_create(self, serializer):
        """Save pet with logged-in user as owner"""
        serializer.save(owner=self.request.user)


class MyPetsView(generics.ListAPIView):
    """
    List all pets owned by the logged-in client.
    """
    serializer_class = MyPetsSerializer
    permission_classes = [permissions.IsAuthenticated, IsClient]

    def get_queryset(self):
        """Return only the client's own pets"""
        return PetProfile.objects.filter(
            owner=self.request.user,
            is_active=True
        ).order_by('-created_at')


class ActivePetsView(generics.ListAPIView):

    serializer_class = PetProfileListSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Return active pets based on user role"""
        user = self.request.user
        
        if user.role == 'CLIENT':
            return PetProfile.objects.filter(
                owner=user,
                is_active=True
            ).order_by('name')
        
        elif user.role == 'VETERINARIAN':
            from appointments.models import Appointment
            treated_pet_ids = Appointment.objects.filter(
                veterinarian=user
            ).values_list('pet_id', flat=True).distinct()
            
            return PetProfile.objects.filter(
                id__in=treated_pet_ids,
                is_active=True
            ).order_by('name')
        
        return PetProfile.objects.none()


class PetsBySpeciesView(generics.ListAPIView):
    """
    List pets filtered by species.
    """
    serializer_class = PetProfileListSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Return pets of specified species for the user"""
        species = self.kwargs.get('species')
        user = self.request.user
        
        if user.role == 'CLIENT':
            return PetProfile.objects.filter(
                owner=user,
                species__iexact=species,
                is_active=True
            ).order_by('name')
        
        elif user.role == 'VETERINARIAN':
            from appointments.models import Appointment
            treated_pet_ids = Appointment.objects.filter(
                veterinarian=user
            ).values_list('pet_id', flat=True).distinct()
            
            return PetProfile.objects.filter(
                id__in=treated_pet_ids,
                species__iexact=species,
                is_active=True
            ).order_by('name')
        
        return PetProfile.objects.none()




