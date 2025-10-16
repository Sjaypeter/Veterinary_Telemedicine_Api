from rest_framework import permissions

class IsPrescriptionOwnerOrDoctor(permissions.BasePermission):
    
    #Allows Clients to view their pets records,and vets to view records they created.
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return (
                request.user == obj.appointment.veterinarian.user or
                request.user == obj.appointment.clienet.user
            )
        # Only vets can modify records
        return request.user.role == 'veterinaraian'