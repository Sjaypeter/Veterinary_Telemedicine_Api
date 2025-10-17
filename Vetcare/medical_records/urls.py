from django.urls import path
from .views import (
    MedicalRecordListView,
    MedicalRecordCreateView,
)

urlpatterns = [
    path("records/", MedicalRecordListView.as_view(), name="medical-record-list"),
    path("records/create/", MedicalRecordCreateView.as_view(), name="medical-record-create"),
]
