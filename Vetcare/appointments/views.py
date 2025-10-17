from django.shortcuts import render
from rest_framework import generics, permissions, status, filters
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.utils import timezone
from .models import Appointment, Consultation
from .serializers import AppointmentSerializer, ConsultationSerializer, Appointmentcreateserializer
from django.contrib.auth import get_user_model
from accounts . permissions import IsVeterinarian, IsClient
from rest_framework import serializers
from accounts . models import Vetprofile, ClientProfile
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.exceptions import ValidationError
# Create your views here.


class Appointmentrequestview(generics.CreateAPIView):
    serializer_class = Appointmentcreateserializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        # The client is the logged-in user
        client = self.request.user
        
        # Get the veterinarian ID from the request data
        vet_id = self.request.data.get('veterinarian')
        
        if not vet_id:
            raise ValidationError({"veterinarian": "This field is required."})
        
        try:
            # Get the veterinarian's profile using the ID from request
            vetprofile = Vetprofile.objects.get(id=vet_id)
        except Vetprofile.DoesNotExist:
            raise ValidationError({"veterinarian": "Veterinarian profile not found."})
        
        # Get the pet ID from request data
        pet_id = self.request.data.get('pet')
        
        if not pet_id:
            raise ValidationError({"pet": "This field is required."})
        
        # Save with the veterinarian PROFILE, not the user
        # Check your model to see if it expects veterinarian (User) or veterinarian (Vetprofile)
        serializer.save(
            client=client,
            veterinarian=vetprofile,  # Changed: pass the profile itself
            pet_id=pet_id
        )




class AppointmentListView(generics.ListAPIView):
    serializer_class = AppointmentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Return only appointments relevant to the logged-in user."""
        user = self.request.user

        if user.role == 'veterinarian':
                return Appointment.objects.filter(veterinarian=user).order_by('-date')
        elif user.role == 'client':
                return Appointment.objects.filter(client=user).order_by('-date')
        
        # If no role, return empty
        return Appointment.objects.none()


class AppointmentUpdateView(generics.UpdateAPIView):
    queryset = Appointment.objects.all()
    serializer_class = AppointmentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def update(self, request, *args, **kwargs):
        """Allow Vet to confirm, cancel, or complete appointment."""
        appointment = self.get_object()
        
        status_choice = request.data.get('status')

        if status_choice not in ['confirmed', 'cancelled', 'completed']:
            return Response(
                {"error": "Invalid status. Must be 'confirmed', 'cancelled', or 'completed'."}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        # Allow doctor to set date/time when confirming
        if status_choice == 'confirmed':
            appointment.date = request.data.get('date', appointment.date)

        appointment.status = status_choice
        appointment.save()
        
        return Response(
            AppointmentSerializer(appointment).data,
            status=status.HTTP_200_OK
        )  

class ConsultationListCreateView(generics.ListCreateAPIView):
    #- GET: List consultations for the logged-in user.
    # POST: Vet can create a consultation after an appointment.

    serializer_class = ConsultationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if getattr(user, "is_vet", False):
            return Consultation.objects.filter(vet=user)
        return Consultation.objects.filter(owner=user)

    def perform_create(self, serializer):
        user = self.request.user

        if not getattr(user, "is_vet", False):
            return Response({"error": "Only veterinarians can create consultations."}, status=status.HTTP_403_FORBIDDEN)

        appointment_id = self.request.data.get('appointment')
        appointment = get_object_or_404(Appointment, id=appointment_id)

        # Ensure this appointment belongs to the vet
        if appointment.vet != user:
            return Response({"error": "You are not authorized to create a consultation for this appointment."}, status=status.HTTP_403_FORBIDDEN)

        serializer.save(vet=user, owner=appointment.owner, pet=appointment.pet)

class ConsultationDetailView(generics.RetrieveUpdateDestroyAPIView):

    #Retrieve, update, or delete a consultation.Only the vet who conducted it or the owner can view it.

    serializer_class = ConsultationSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = Consultation.objects.all()

    def get_object(self):
        consultation = get_object_or_404(Consultation, pk=self.kwargs['pk'])
        user = self.request.user

        if consultation.vet != user and consultation.owner != user:
            self.permission_denied(self.request, message="You are not authorized to access this consultation.")
        return consultation

    def update(self, request, *args, **kwargs):
        consultation = self.get_object()
        if consultation.vet != request.user:
            return Response({"error": "Only the veterinarian can update this consultation."}, status=status.HTTP_403_FORBIDDEN)
        return super().update(request, *args, **kwargs)


class OwnerConsultationHistoryView(generics.ListAPIView):
    
    #List all past consultations for the logged-in pet owner.
    
    serializer_class = ConsultationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if not getattr(user, "is_owner", False):
            self.permission_denied(self.request, message="Only pet owners can access this view.")
        return Consultation.objects.filter(owner=user)


    

    


