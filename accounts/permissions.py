from rest_framework import permissions


class IsVeterinarian(permissions.BasePermission):
    """
    Allows access only to authenticated users with veterinarian role.
    """
    
    message = "Only veterinarians can perform this action."
    
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            request.user.role == 'VETERINARIAN'
        )
    
    def has_object_permission(self, request, view, obj):
        """Check if the veterinarian owns this object"""
        # If object has a 'veterinarian' attribute, check ownership
        if hasattr(obj, 'veterinarian'):
            return obj.veterinarian == request.user
        # If object has a 'user' attribute, check if it's the same user
        if hasattr(obj, 'user'):
            return obj.user == request.user
        # Default: allow access if they have general permission
        return self.has_permission(request, view)


class IsClient(permissions.BasePermission):
    """
    Allows access only to authenticated users with client role.
    """
    
    message = "Only clients can perform this action."
    
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            request.user.role == 'CLIENT'
        )
    
    def has_object_permission(self, request, view, obj):
        """Check if the client owns this object"""
        # If object has a 'client' attribute, check ownership
        if hasattr(obj, 'client'):
            return obj.client == request.user
        # If object has a 'user' attribute, check if it's the same user
        if hasattr(obj, 'user'):
            return obj.user == request.user
        # Default: allow access if they have general permission
        return self.has_permission(request, view)


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Object-level permission to only allow owners to edit objects.
    Assumes the model instance has a 'user' or 'owner' attribute.
    """
    
    message = "You can only modify your own content."
    
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed for any request
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write permissions only allowed to the owner
        if hasattr(obj, 'user'):
            return obj.user == request.user
        if hasattr(obj, 'owner'):
            return obj.owner == request.user
        if hasattr(obj, 'client'):
            return obj.client == request.user
        
        return False


class IsVeterinarianOrReadOnly(permissions.BasePermission):
    """
    Allows veterinarians full access, others get read-only access.
    """
    
    message = "Only veterinarians can modify this content."
    
    def has_permission(self, request, view):
        # Read permissions for any authenticated user
        if request.method in permissions.SAFE_METHODS:
            return request.user and request.user.is_authenticated
        
        # Write permissions only for veterinarians
        return (
            request.user and 
            request.user.is_authenticated and 
            request.user.role == 'VETERINARIAN'
        )


class IsAppointmentParticipant(permissions.BasePermission):
    """
    Allow access to appointment only if user is the client or veterinarian.
    """
    
    message = "You can only access your own appointments."
    
    def has_object_permission(self, request, view, obj):
        # Check if user is either the client or veterinarian in the appointment
        return (
            request.user.is_authenticated and 
            (obj.client == request.user or obj.veterinarian == request.user)
        )