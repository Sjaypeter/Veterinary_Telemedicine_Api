from django.urls import path
from .views import (
    MedicalRecordListView,
    MedicalRecordDetailView,
    MedicalRecordCreateView,
    PetMedicalHistoryView,
    MyPetsMedicalRecordsView,
    RecentMedicalRecordsView,
    FollowUpRequiredView,
)

app_name = 'medical_records'

urlpatterns = [
    path('', MedicalRecordListView.as_view(), name='medical-record-list'),
    path('create/', MedicalRecordCreateView.as_view(), name='medical-record-create'),
    path('<int:pk>/', MedicalRecordDetailView.as_view(), name='medical-record-detail'),
    
    path('pet/<int:pet_id>/history/', PetMedicalHistoryView.as_view(), name='pet-medical-history'),
    path('my-pets/', MyPetsMedicalRecordsView.as_view(), name='my-pets-records'),

    path('recent/', RecentMedicalRecordsView.as_view(), name='recent-records'),
    path('follow-ups/', FollowUpRequiredView.as_view(), name='follow-up-required'),
]