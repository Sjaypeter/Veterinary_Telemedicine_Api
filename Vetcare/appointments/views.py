from django.shortcuts import render
from rest_framework import generics, permissions, status, filters
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.utils import timezone
from .models import Appointment, Consultation
from .serializers import AppointmentSerializer, ConsultationSerializer
from django.contrib.auth import get_user_model


# Create your views here.

User = get_user_model()


class AppointmentListCreateView(generics.ListCreateAPIView):
    """
    - GET: List appointments for the logged-in user.
    - POST: Create a new appointment.
    """
    serializer_class = AppointmentSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['reason', 'pet__name']
    ordering_fields = ['appointment_date', 'created_at']

    def get_queryset(self):
        user = self.request.user
        # Vet sees appointments assigned to them, Owner sees their own
        if user.is_vet:
            return Appointment.objects.filter(vet=user).order_by('-appointment_date')
        return Appointment.objects.filter(owner=user).order_by('-appointment_date')

    def perform_create(self, serializer):
        
       # Automatically assign the logged-in owner as the creator. Vet can be selected from the request.
        serializer.save(owner=self.request.user)



class AppointmentDetailView(generics.RetrieveUpdateDestroyAPIView):

    #Retrieve, update, or cancel an appointment. Only the owner or assigned vet can modify.


    serializer_class = AppointmentSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = Appointment.objects.all()

    def get_object(self):
        appointment = get_object_or_404(Appointment, pk=self.kwargs['pk'])
        user = self.request.user

        # Only allow the owner or vet to access this record
        if appointment.owner != user and appointment.vet != user:
            self.permission_denied(self.request, message="Not authorized to access this appointment.")
        return appointment

    def delete(self, request, *args, **kwargs):

        #mark the appointment as cancelled

        appointment = self.get_object()
        appointment.status = 'Cancelled'
        appointment.save()
        return Response({"message": "Appointment cancelled successfully."}, status=status.HTTP_200_OK)
    

class VetUpcomingAppointmentsView(generics.ListAPIView):
    
    #List all upcoming appointments for the logged-in vet.

    serializer_class = AppointmentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if not user.is_vet:
            self.permission_denied(self.request, message="Only veterinarians can access this view.")
        return Appointment.objects.filter(vet=user, appointment_date__gte=timezone.now(), status='Scheduled').order_by('appointment_date')

class OwnerPastAppointmentsView(generics.ListAPIView):
    
    #List all past (completed or cancelled) appointments for a pet owner.
    
    serializer_class = AppointmentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if not user.is_client:
            self.permission_denied(self.request, message="Only pet owners can access this view.")
        return Appointment.objects.filter(owner=user, appointment_date__lt=timezone.now()).order_by('-appointment_date')
    

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


class VetFollowUpListView(generics.ListAPIView):
    
    #List upcoming follow-up consultations for the logged-in vet.

    serializer_class = ConsultationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if not getattr(user, "is_vet", False):
            self.permission_denied(self.request, message="Only veterinarians can access this view.")
        return Consultation.objects.filter(
            vet=user,
            is_follow_up_required=True,
            follow_up_date__gte=timezone.now()
        ) #set up follow up order filter
    

    


