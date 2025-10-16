from django.urls import path
from .views import PetListCreateView, PetDetailView

urlpatterns = [
    path('Petprofile/', PetListCreateView.as_view(), name='pet-list-create'),
    path('<int:pk>/', PetDetailView.as_view(), name='pet-detail'),
]
