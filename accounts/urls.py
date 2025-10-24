from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (
    # Authentication
    UserRegistrationView,
    UserLoginView,
    UserLogoutView,
    CurrentUserView,
    # Client Profiles
    ClientProfileListView,
    ClientProfileDetailView,
    MyClientProfileView,
    # Vet Profiles
    VetProfileListView,
    VetProfileDetailView,
    MyVetProfileView,
    VetProfileUpdateView,
    # User Management
    UserListView,
    UserDetailView,
)

app_name = 'accounts'

urlpatterns = [
    # AUTHENTICATION 
    path('auth/register/', UserRegistrationView.as_view(), name='register'),
    path('auth/login/', UserLoginView.as_view(), name='login'),
    path('auth/logout/', UserLogoutView.as_view(), name='logout'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
    path('auth/me/', CurrentUserView.as_view(), name='current-user'),
    
    # CLIENT PROFILES 
    path('clients/', ClientProfileListView.as_view(), name='client-list'),
    path('clients/<int:pk>/', ClientProfileDetailView.as_view(), name='client-detail'),
    path('profile/client/me/', MyClientProfileView.as_view(), name='my-client-profile'),
    
    #VET PROFILES
    path('veterinarians/', VetProfileListView.as_view(), name='vet-list'),
    path('veterinarians/<int:pk>/', VetProfileDetailView.as_view(), name='vet-detail'),
    path('veterinarians/<int:pk>/update/', VetProfileUpdateView.as_view(), name='vet-update'),
    path('profile/vet/me/', MyVetProfileView.as_view(), name='my-vet-profile'),
    
    #USER MANAGEMENT 
    path('users/', UserListView.as_view(), name='user-list'),
    path('users/<int:pk>/', UserDetailView.as_view(), name='user-detail'),
]