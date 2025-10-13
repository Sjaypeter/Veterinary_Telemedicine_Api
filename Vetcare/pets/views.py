from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from .models import PetProfile
from .serializers import PetSerializer
from accounts.models import CustomUser


class PetListCreateView(generics.ListCreateAPIView):
    """
    GET: List all pets belonging to the authenticated user.
    POST: Create a new pet and assign it to the authenticated user.
    """
    serializer_class = PetSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Return only the pets owned by the logged-in user
        return PetProfile.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        # Automatically assign the current user as the owner
        serializer.save(owner=self.request.user)


class PetDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET: Retrieve pet details by ID.
    PUT/PATCH: Update pet information (only if owner).
    DELETE: Delete pet (only if owner).
    """
    serializer_class = PetSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Allow access only to the user's own pets
        return PetProfile.objects.filter(owner=self.request.user)

    def delete(self, request, *args, **kwargs):
        pet = self.get_object()
        if pet.owner != request.user:
            return Response({'detail': 'You do not have permission to delete this pet.'}, status=status.HTTP_403_FORBIDDEN)
        return super().delete(request, *args, **kwargs)
