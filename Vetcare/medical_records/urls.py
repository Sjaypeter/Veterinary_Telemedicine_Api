from django.urls import path
from .views import (
    MedicalRecordListView,
    MedicalRecordCreateView,
    VaccinationListCreateView,
    VaccinationDetailView,
)

urlpatterns = [
    path("records/", MedicalRecordListView.as_view(), name="medical-record-list"),
    path("records/create/", MedicalRecordCreateView.as_view(), name="medical-record-create"),
    path("vaccinations/", VaccinationListCreateView.as_view(), name="vaccination-list-create"),
    path("vaccinations/<int:pk>/", VaccinationDetailView.as_view(), name="vaccination-detail"),
]
