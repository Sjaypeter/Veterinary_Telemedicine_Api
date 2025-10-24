from django.urls import path
from .views import (
    PetListView,
    PetDetailView,
    PetCreateView,
    MyPetsView,
    ActivePetsView,
    PetsBySpeciesView,
)

app_name = 'pets'

urlpatterns = [
    path('pet/', PetListView.as_view(), name='pet-list'),
    path('pet/create/', PetCreateView.as_view(), name='pet-create'),
    path('pet/<int:pk>/', PetDetailView.as_view(), name='pet-detail'),
    
    path('my-pets/', MyPetsView.as_view(), name='my-pets'),
    path('active/', ActivePetsView.as_view(), name='active-pets'),
    path('species/<str:species>/', PetsBySpeciesView.as_view(), name='pets-by-species'),
]