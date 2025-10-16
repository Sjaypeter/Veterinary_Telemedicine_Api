from django.urls import path
from . views import RegisterView,ClientprofileView,ClientprofiledetailView,VetprofiledetailView,Vetprofileview
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),


    path('veterinarian/', views.Vetprofileview.as_view(), name='vet-list'),
    path('veterinarian/<int:pk>/', views.VetprofiledetailView.as_view(), name='vet-detail'),


    path('client/', views.ClientprofileView.as_view(), name='client-list'),
    path('client/<int:pk>/', views.ClientprofiledetailView.as_view(), name='client-detail'),

    path('login/', auth_views.LoginView.as_view(template_name='accounts/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout')

]
