from django.urls import path
from .views import PetprofiledetailView, Petprofileview

urlpatterns = [
    path('petprofile/', Petprofileview.as_view(), name='pet-list'),
    path('petprofile/<int:pk>/', PetprofiledetailView.as_view(), name='pet-detail'),
]
