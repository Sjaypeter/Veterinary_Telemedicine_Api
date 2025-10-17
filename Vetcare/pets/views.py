from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from .models import PetProfile
from .serializers import Petprofilecreateserializer, Petprofileserializer
from accounts.models import CustomUser
from accounts . permissions import IsClient


class Petprofileview(generics.ListAPIView):
    queryset = PetProfile.objects.all()
    serializer_class = Petprofileserializer
    permission_classes = [permissions.IsAuthenticated]


class PetprofiledetailView(generics.RetrieveUpdateAPIView):
    serializer_class = Petprofileserializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        #Only clients allowed to alter this
        user = self.request.user
        if user.role == 'client':
            return PetProfile.objects.filter(user=user)
        return PetProfile.objects.none()
