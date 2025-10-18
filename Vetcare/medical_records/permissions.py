from rest_framework import permissions


class CanViewMedicalRecord(permissions.BasePermission):
    """
    Allow viewing medical records if user is either:
    - The veterinarian who created the record
    - The owner of the pet
    """
    
    message = "You can only view medical records for your pets or records you created."
    
    def has_permission(self, request, view):
        """Check if user is authenticated"""
        return request.user and request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        """Check if user has access to this medical record"""
        user = request.user
        
        # Pet owner can view their pet's records
        if obj.pet.owner == user:
            return True
        
        # Veterinarian who created the record can view it
        if obj.veterinarian == user:
            return True
        
        return False



class IsMedicalRecordParticipant(permissions.BasePermission):
    """
    Combined permission for medical records:
    - Pet owners can view
    - Veterinarians who created it can view and modify
    """
    
    message = "You can only access medical records you're involved with."
    
    def has_permission(self, request, view):
        """Check if user is authenticated"""
        return request.user and request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        """Check permissions based on action and user role"""
        user = request.user
        
        # Read permissions - pet owner or veterinarian
        if request.method in permissions.SAFE_METHODS:
            return (
                obj.pet.owner == user or 
                obj.veterinarian == user
            )
        
        # Write permissions - only the veterinarian who created it
        return (
            user.role == 'VETERINARIAN' and 
            obj.veterinarian == user
        )


class CanCreateMedicalRecord(permissions.BasePermission):
    """
    Only veterinarians can create medical records.
    """
    
    message = "Only veterinarians can create medical records."
    
    def has_permission(self, request, view):
        """Check if user is a veterinarian"""
        return (
            request.user and 
            request.user.is_authenticated and
            request.user.role == 'VETERINARIAN'
        )


class CanViewVaccination(permissions.BasePermission):
    """
    Allow viewing vaccinations if user is:
    - The pet owner
    - The veterinarian who administered it
    """
    
    message = "You can only view vaccinations for your pets or vaccinations you administered."
    
    def has_permission(self, request, view):
        """Check if user is authenticated"""
        return request.user and request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        """Check if user has access to this vaccination"""
        user = request.user
        
        # Pet owner can view
        if obj.pet.owner == user:
            return True
        
        # Veterinarian who administered it can view
        if obj.veterinarian == user:
            return True
        
        return False


class CanModifyVaccination(permissions.BasePermission):
    """
    Only the veterinarian who administered the vaccination can modify it.
    """
    
    message = "Only the veterinarian who administered this vaccination can modify it."
    
    def has_permission(self, request, view):
        """Check if user is a veterinarian"""
        return (
            request.user and 
            request.user.is_authenticated and
            request.user.role == 'VETERINARIAN'
        )
    
    def has_object_permission(self, request, view, obj):
        """Check if user is the veterinarian who administered it"""
        return (
            request.user.is_authenticated and
            obj.veterinarian == request.user
        )


class CanAccessPetMedicalHistory(permissions.BasePermission):
    """
    Allow access to pet medical history if:
    - User is the pet owner
    - User is a veterinarian who has treated the pet
    """
    
    message = "You can only access medical history for your own pets or pets you've treated."
    
    def has_permission(self, request, view):
        """Check if user is authenticated and validate pet access"""
        if not (request.user and request.user.is_authenticated):
            return False
        
        # Get pet_id from URL kwargs
        pet_id = view.kwargs.get('pet_id')
        if not pet_id:
            return False
        
        from pets.models import PetProfile
        try:
            pet = PetProfile.objects.get(id=pet_id)
        except PetProfile.DoesNotExist:
            return False
        
        user = request.user
        
        # Pet owner has access
        if pet.owner == user:
            return True
        
        # Veterinarians who have treated this pet have access
        if user.role == 'VETERINARIAN':
            from .models import MedicalRecord
            has_treated = MedicalRecord.objects.filter(
                pet=pet,
                veterinarian=user
            ).exists()
            return has_treated
        
        return False