from rest_framework import permissions


class clientorvetappointment(permissions.BasePermission):
    #Allows to view appointments and vets to manage theirs

    def has_object_permission(self, request, view, obj):
        return (
            request.user == obj.client or
            request.user == obj.veterinarian
        )
    
class Vetconsult(permissions.BasePermission):
    #Allows vet assigned to consult

    def has_object_permission(self, request, view, obj):
        return request.user == obj.veterinarian