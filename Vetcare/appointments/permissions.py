from rest_framework import permissions


class IsAppointmentParticipant(permissions.BasePermission):
    """
    Allow access to appointment only if user is the client or veterinarian.
    Both clients and veterinarians can view their appointments.
    """
    
    message = "You can only access appointments where you are the client or veterinarian."
    
    def has_permission(self, request, view):
        """Check if user is authenticated"""
        return request.user and request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        """Check if user is either the client or veterinarian in the appointment"""
        return (
            request.user.is_authenticated and 
            (obj.client == request.user or obj.veterinarian == request.user)
        )


class IsAppointmentVeterinarian(permissions.BasePermission):
    """
    Allow only the assigned veterinarian to modify appointment details.
    Used for confirming, updating status, or completing appointments.
    """
    
    message = "Only the assigned veterinarian can modify this appointment."
    
    def has_permission(self, request, view):
        """Check if user is authenticated and is a veterinarian"""
        return (
            request.user and 
            request.user.is_authenticated and 
            request.user.role == 'VETERINARIAN'
        )
    
    def has_object_permission(self, request, view, obj):
        """Check if user is the veterinarian assigned to this appointment"""
        return (
            request.user.is_authenticated and 
            obj.veterinarian == request.user
        )


class IsAppointmentClient(permissions.BasePermission):
    """
    Allow only the client who created the appointment to cancel it.
    Clients can cancel their own pending or confirmed appointments.
    """
    
    message = "Only the client who created this appointment can cancel it."
    
    def has_permission(self, request, view):
        """Check if user is authenticated and is a client"""
        return (
            request.user and 
            request.user.is_authenticated and 
            request.user.role == 'CLIENT'
        )
    
    def has_object_permission(self, request, view, obj):
        """Check if user is the client who created the appointment"""
        return (
            request.user.is_authenticated and 
            obj.client == request.user
        )


class IsConsultationVeterinarian(permissions.BasePermission):
    """
    Allow only the veterinarian who conducted the consultation to view/edit it.
    """
    
    message = "Only the veterinarian who conducted this consultation can access it."
    
    def has_permission(self, request, view):
        """Check if user is authenticated and is a veterinarian"""
        return (
            request.user and 
            request.user.is_authenticated and 
            request.user.role == 'VETERINARIAN'
        )
    
    def has_object_permission(self, request, view, obj):
        """Check if user is the veterinarian assigned to this consultation"""
        return (
            request.user.is_authenticated and 
            obj.veterinarian == request.user
        )


class CanViewConsultation(permissions.BasePermission):
    """
    Allow consultation viewing by:
    - The veterinarian who created it
    - The client whose pet was consulted
    """
    
    message = "You can only view consultations for your own appointments."
    
    def has_permission(self, request, view):
        """Check if user is authenticated"""
        return request.user and request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        """Check if user is the vet or the client of the consultation"""
        return (
            request.user.is_authenticated and 
            (obj.veterinarian == request.user or obj.appointment.client == request.user)
        )


class CanCreateConsultation(permissions.BasePermission):
    """
    Only veterinarians can create consultations for completed appointments.
    """
    
    message = "Only veterinarians can create consultations for completed appointments."
    
    def has_permission(self, request, view):
        """Check if user is authenticated and is a veterinarian"""
        return (
            request.user and 
            request.user.is_authenticated and 
            request.user.role == 'VETERINARIAN'
        )


class IsAppointmentParticipantOrReadOnly(permissions.BasePermission):
    """
    Allow read access to appointment participants.
    Only veterinarians can modify.
    """
    
    message = "You must be involved in this appointment to view it."
    
    def has_permission(self, request, view):
        """Check if user is authenticated"""
        return request.user and request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        """
        Read permissions for participants.
        Write permissions only for the veterinarian.
        """
        # Check if user is participant
        is_participant = (obj.client == request.user or obj.veterinarian == request.user)
        
        # Read-only for any participant
        if request.method in permissions.SAFE_METHODS:
            return is_participant
        
        # Write permissions only for veterinarian
        return obj.veterinarian == request.user