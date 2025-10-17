from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from django.utils import timezone

from .models import Appointment, Consultation
from .serializers import (AppointmentListSerializer,AppointmentDetailSerializer,AppointmentCreateSerializer,AppointmentUpdateSerializer,
                          AppointmentStatusUpdateSerializer,ConsultationSerializer,ConsultationListSerializer)
from .permissions import (IsAppointmentParticipant,IsAppointmentVeterinarian,IsAppointmentClient,IsConsultationVeterinarian,CanViewConsultation)
from accounts.permissions import IsVeterinarian, IsClient
from accounts.models import Vetprofile


# APPOINTMENT VIEWS

class AppointmentCreateView(generics.CreateAPIView):
    """
    Create a new appointment (Client only).
    """
    serializer_class = AppointmentCreateSerializer
    permission_classes = [permissions.IsAuthenticated, IsClient]

    def perform_create(self, serializer):
        """Save appointment with the logged-in user as client"""
        serializer.save(client=self.request.user)


class AppointmentListView(generics.ListAPIView):
    """List appointments for the logged-in user. """
    serializer_class = AppointmentListSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Return appointments based on user role"""
        user = self.request.user
        
        if user.role == 'VETERINARIAN':
            return Appointment.objects.filter(
                veterinarian=user
            ).select_related('client', 'veterinarian', 'pet').order_by('-date', '-created_at')
        
        elif user.role == 'CLIENT':
            return Appointment.objects.filter(
                client=user
            ).select_related('client', 'veterinarian', 'pet').order_by('-date', '-created_at')
        
        return Appointment.objects.none()


class AppointmentDetailView(generics.RetrieveAPIView):
    """ View detailed information about a specific appointment """

    queryset = Appointment.objects.select_related('client', 'veterinarian', 'pet').all()
    serializer_class = AppointmentDetailSerializer
    permission_classes = [permissions.IsAuthenticated, IsAppointmentParticipant]


class AppointmentUpdateView(generics.UpdateAPIView):
    """ Update appointment (Veterinarian only). """
    queryset = Appointment.objects.all()
    serializer_class = AppointmentUpdateSerializer
    permission_classes = [permissions.IsAuthenticated, IsAppointmentVeterinarian]

    def update(self, request, *args, **kwargs):
        """Update appointment with validation"""
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        
        # Return detailed response
        return Response(
            AppointmentDetailSerializer(instance).data,
            status=status.HTTP_200_OK
        )


class AppointmentConfirmView(generics.UpdateAPIView):
    """Confirm an appointment (Veterinarian only)."""
    queryset = Appointment.objects.all()
    permission_classes = [permissions.IsAuthenticated, IsAppointmentVeterinarian]

    def update(self, request, *args, **kwargs):
        appointment = self.get_object()
        
        # Validate current status
        if appointment.status != Appointment.PENDING:
            return Response(
                {"error": "Only pending appointments can be confirmed."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Update appointment
        appointment.status = Appointment.CONFIRMED
        appointment.date = request.data.get('date', appointment.date)
        appointment.time = request.data.get('time', appointment.time)
        
        # Validate before saving
        try:
            appointment.full_clean()
            appointment.save()
        except ValidationError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        return Response(
            AppointmentDetailSerializer(appointment).data,
            status=status.HTTP_200_OK
        )


class AppointmentCompleteView(generics.UpdateAPIView):
    """Mark an appointment as completed (Veterinarian only)"""
    queryset = Appointment.objects.all()
    permission_classes = [permissions.IsAuthenticated, IsAppointmentVeterinarian]

    def update(self, request, *args, **kwargs):
        appointment = self.get_object()
        
        # Validate current status
        if appointment.status != Appointment.CONFIRMED:
            return Response(
                {"error": "Only confirmed appointments can be marked as completed."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Update status
        appointment.status = Appointment.COMPLETED
        appointment.save()
        
        return Response(
            AppointmentDetailSerializer(appointment).data,
            status=status.HTTP_200_OK
        )


class AppointmentCancelView(generics.UpdateAPIView):
    """Cancel an appointment"""
    queryset = Appointment.objects.all()
    permission_classes = [permissions.IsAuthenticated, IsAppointmentParticipant]

    def update(self, request, *args, **kwargs):
        appointment = self.get_object()
        user = request.user
        
        # Check if appointment can be cancelled
        if not appointment.can_be_cancelled:
            return Response(
                {"error": "This appointment cannot be cancelled."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Verify user is either client or vet
        if user != appointment.client and user != appointment.veterinarian:
            return Response(
                {"error": "You are not authorized to cancel this appointment."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        appointment.status = Appointment.CANCELLED
        appointment.save()
        
        return Response(
            AppointmentDetailSerializer(appointment).data,
            status=status.HTTP_200_OK
        )


# CONSULTATION VIEWS

class ConsultationCreateView(generics.CreateAPIView):
    #Create a consultation after completing an appointment (Veterinarian only).
    serializer_class = ConsultationSerializer
    permission_classes = [permissions.IsAuthenticated, IsVeterinarian]

    def perform_create(self, serializer):
        """Save consultation with the logged-in vet"""
        serializer.save(veterinarian=self.request.user)


class ConsultationListView(generics.ListAPIView):
    #List consultations for the logged-in user.
    serializer_class = ConsultationListSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Return consultations based on user role"""
        user = self.request.user
        
        if user.role == 'VETERINARIAN':
            return Consultation.objects.filter(
                veterinarian=user
            ).select_related('appointment', 'veterinarian').order_by('-created_at')
        
        elif user.role == 'CLIENT':
            return Consultation.objects.filter(
                appointment__client=user
            ).select_related('appointment', 'veterinarian').order_by('-created_at')
        
        return Consultation.objects.none()


class ConsultationDetailView(generics.RetrieveUpdateAPIView):
    """View or update a consultation."""
    queryset = Consultation.objects.select_related('appointment', 'veterinarian').all()
    serializer_class = ConsultationSerializer
    permission_classes = [permissions.IsAuthenticated, CanViewConsultation]

    def get_permissions(self):
        """Only vets can update consultations"""
        if self.request.method in ['PUT', 'PATCH']:
            return [permissions.IsAuthenticated(), IsConsultationVeterinarian()]
        return [permissions.IsAuthenticated(), CanViewConsultation()]


class ClientConsultationHistoryView(generics.ListAPIView):
    """
    List all consultations for the logged-in client's pets.
    """
    serializer_class = ConsultationListSerializer
    permission_classes = [permissions.IsAuthenticated, IsClient]

    def get_queryset(self):
        """Return all consultations for the client's pets"""
        return Consultation.objects.filter(
            appointment__client=self.request.user
        ).select_related('appointment', 'veterinarian').order_by('-created_at')


class VetConsultationHistoryView(generics.ListAPIView):
    """
    List all consultations created by the logged-in veterinarian.
    """
    serializer_class = ConsultationListSerializer
    permission_classes = [permissions.IsAuthenticated, IsVeterinarian]

    def get_queryset(self):
        """Return all consultations created by this vet"""
        return Consultation.objects.filter(
            veterinarian=self.request.user
        ).select_related('appointment', 'veterinarian').order_by('-created_at')


class PendingAppointmentsView(generics.ListAPIView):
    """
    List pending appointments (Veterinarian only).
    """
    serializer_class = AppointmentListSerializer
    permission_classes = [permissions.IsAuthenticated, IsVeterinarian]

    def get_queryset(self):
        """Return pending appointments for this vet"""
        return Appointment.objects.filter(
            veterinarian=self.request.user,
            status=Appointment.PENDING
        ).select_related('client', 'pet').order_by('date', 'created_at')


class UpcomingAppointmentsView(generics.ListAPIView):
    """
    List upcoming confirmed appointments.
    """
    serializer_class = AppointmentListSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Return upcoming appointments for the user"""
        user = self.request.user
        today = timezone.now().date()
        
        base_query = Appointment.objects.filter(
            status=Appointment.CONFIRMED,
            date__gte=today
        ).select_related('client', 'veterinarian', 'pet')
        
        if user.role == 'VETERINARIAN':
            return base_query.filter(veterinarian=user).order_by('date', 'time')
        
        elif user.role == 'CLIENT':
            return base_query.filter(client=user).order_by('date', 'time')
        
        return Appointment.objects.none()