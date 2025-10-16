from rest_framework import permissions


class IsVeterinarian(permissions.BasePermission):
    #Allows access only to users with vet role
    
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'veterinarian'
    

class IsClient(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'client'