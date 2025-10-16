from django.urls import path
from .views import (AppointmentListView, Appointmentrequestview, AppointmentUpdateView)
from .views import (ConsultationListCreateView,ConsultationDetailView,OwnerConsultationHistoryView)

urlpatterns = [
    path('appointment/requests/', Appointmentrequestview.as_view(), name='appointment-request'),
    path('appointment/', AppointmentListView.as_view(), name='appointment-list'),
    path('appointment/<int:pk>/update/', AppointmentUpdateView.as_view(), name = 'appointment-update'),
    



    path('consultations/', ConsultationListCreateView.as_view(), name='consultation-list-create'),
    path('consultations/<int:pk>/', ConsultationDetailView.as_view(), name='consultation-detail'),
    path('consultations/owner/history/', OwnerConsultationHistoryView.as_view(), name='owner-consultation-history'),
]
