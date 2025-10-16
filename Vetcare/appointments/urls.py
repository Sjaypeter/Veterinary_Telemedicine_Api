from django.urls import path
from .views import (AppointmentListCreateView,AppointmentDetailView,VetUpcomingAppointmentsView,OwnerPastAppointmentsView)
from .views import (ConsultationListCreateView,ConsultationDetailView,OwnerConsultationHistoryView,VetFollowUpListView)

urlpatterns = [
    path('Appointment/', AppointmentListCreateView.as_view(), name='appointment-list-create'),
    path('<int:pk>/', AppointmentDetailView.as_view(), name='appointment-detail'),
    path('vet/upcoming/', VetUpcomingAppointmentsView.as_view(), name='vet-upcoming'),
    path('owner/past/', OwnerPastAppointmentsView.as_view(), name='owner-past'),
    path('consultations/', ConsultationListCreateView.as_view(), name='consultation-list-create'),
    path('consultations/<int:pk>/', ConsultationDetailView.as_view(), name='consultation-detail'),
    path('consultations/owner/history/', OwnerConsultationHistoryView.as_view(), name='owner-consultation-history'),
    path('consultations/vet/follow-ups/', VetFollowUpListView.as_view(), name='vet-follow-up-list'),
]
