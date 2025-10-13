from django.urls import path
from .views import (
    MedicalRecordListCreateView,
    MedicalRecordDetailView,
    VaccinationListCreateView,
    VaccinationDetailView
)

urlpatterns = [
    path("records/", MedicalRecordListCreateView.as_view(), name="medical-record-list-create"),
    path("records/<int:pk>/", MedicalRecordDetailView.as_view(), name="medical-record-detail"),
    path("vaccinations/", VaccinationListCreateView.as_view(), name="vaccination-list-create"),
    path("vaccinations/<int:pk>/", VaccinationDetailView.as_view(), name="vaccination-detail"),
]
