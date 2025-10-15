from django.urls import path
from . views import RegisterView,LoginView,UserListView,UserProfileView


urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    #path('login/', LoginView.as_view(), name='login'),
    path('me/', UserProfileView.as_view(), name='user-profile'),
    path('users/', UserListView.as_view(), name='user-list'),
]
