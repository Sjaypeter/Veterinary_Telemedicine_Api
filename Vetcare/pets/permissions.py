from rest_framework import permissions


class IsPetOwner(permissions.BasePermission):
    """
    Allow access only to the pet owner.
    """
    
    message = "You can only access your own pets."
    
    def has_permission(self, request, view):
        """Check if user is authenticated"""
        return request.user and request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        """Check if user is the pet owner"""
        return (
            request.user.is_authenticated and
            obj.owner == request.user
        )


class IsPetOwnerOrVet(permissions.BasePermission):
    """
    Allow pet owners to view and modify their pets.
    Allow veterinarians to view pets (read-only).
    """
    
    message = "You can only access pets you own or have treated."
    
    def has_permission(self, request, view):
        """Check if user is authenticated"""
        return request.user and request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        """Check permissions based on user role and request method"""
        user = request.user
        
        # Pet owner has full access
        if obj.owner == user:
            return True
        
        # Veterinarians can view pets they've treated
        if user.role == 'VETERINARIAN' and request.method in permissions.SAFE_METHODS:
            # Check if vet has treated this pet
            from appointments.models import Appointment
            has_treated = Appointment.objects.filter(
                pet=obj,
                veterinarian=user
            ).exists()
            return has_treated
        
        return False


class CanCreatePet(permissions.BasePermission):
    """
    Only clients can create pet profiles.
    """
    
    message = "Only clients can create pet profiles."
    
    def has_permission(self, request, view):
        """Check if user is a client"""
        return (
            request.user and 
            request.user.is_authenticated and
            request.user.role == 'CLIENT'
        )


class CanModifyPet(permissions.BasePermission):
    """
    Only the pet owner can modify the pet profile.
    """
    
    message = "Only the pet owner can modify this profile."
    
    def has_permission(self, request, view):
        """Check if user is authenticated"""
        return request.user and request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        """Check if user is the pet owner"""
        return (
            request.user.is_authenticated and
            obj.owner == request.user
        )


class CanViewPet(permissions.BasePermission):
    """
    Allow viewing pet if user is:
    - The pet owner
    - A veterinarian who has treated the pet
    - A veterinarian viewing through an appointment
    """
    
    message = "You can only view pets you own or have treated."
    
    def has_permission(self, request, view):
        """Check if user is authenticated"""
        return request.user and request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        """Check if user has access to view this pet"""
        user = request.user
        
        # Pet owner can view
        if obj.owner == user:
            return True
        
        # Veterinarians who have treated this pet can view
        if user.role == 'VETERINARIAN':
            from appointments.models import Appointment
            from medical_records.models import MedicalRecord
            
            # Check appointments
            has_appointment = Appointment.objects.filter(
                pet=obj,
                veterinarian=user
            ).exists()
            
            # Check medical records
            has_records = MedicalRecord.objects.filter(
                pet=obj,
                veterinarian=user
            ).exists()
            
            return has_appointment or has_records
        
        return False


class IsPetOwnerOrReadOnlyForVet(permissions.BasePermission):
    """
    Combined permission:
    - Pet owners have full CRUD access to their pets
    - Veterinarians who have treated the pet have read-only access
    """
    
    message = "You can only modify pets you own."
    
    def has_permission(self, request, view):
        """Check if user is authenticated"""
        return request.user and request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        """Check permissions based on action and user role"""
        user = request.user
        
        # Pet owner has full access (read and write)
        if obj.owner == user:
            return True
        
        # Veterinarians have read-only access if they've treated the pet
        if user.role == 'VETERINARIAN' and request.method in permissions.SAFE_METHODS:
            from appointments.models import Appointment
            from medical_records.models import MedicalRecord
            
            # Check if vet has treated this pet
            has_treated = (
                Appointment.objects.filter(pet=obj, veterinarian=user).exists() or
                MedicalRecord.objects.filter(pet=obj, veterinarian=user).exists()
            )
            return has_treated
        
        return False


class CanAccessPetList(permissions.BasePermission):
    """
    Permission for listing pets:
    - Clients see only their own pets
    - Veterinarians see pets they've treated
    """
    
    message = "You can only list pets you own or have treated."
    
    def has_permission(self, request, view):
        """Check if user is authenticated"""
        return request.user and request.user.is_authenticated


class IsClientWithOwnPets(permissions.BasePermission):
    """
    Ensure client is only accessing their own pets when creating/updating.
    Used for validating ownership during create/update operations.
    """
    
    message = "You can only manage your own pets."
    
    def has_permission(self, request, view):
        """Check if user is a client"""
        if not (request.user and request.user.is_authenticated):
            return False
        
        # For list/retrieve, allow through (object permission will handle it)
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # For create/update, must be a client
        return request.user.role == 'CLIENT'
    
    def has_object_permission(self, request, view, obj):
        """Check if user owns the pet"""
        return obj.owner == request.user