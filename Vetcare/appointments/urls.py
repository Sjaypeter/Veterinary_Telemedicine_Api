from django.urls import path
from .views import (
    AppointmentCreateView,
    AppointmentListView,
    AppointmentDetailView,
    AppointmentUpdateView,
    AppointmentConfirmView,
    AppointmentCompleteView,
    AppointmentCancelView,
    PendingAppointmentsView,
    UpcomingAppointmentsView,

    ConsultationCreateView,
    ConsultationListView,
    ConsultationDetailView,
    ClientConsultationHistoryView,
    VetConsultationHistoryView,
)

app_name = 'appointments'

urlpatterns = [
    path('appointment/', AppointmentListView.as_view(), name='appointment-list'),
    path('appointment/create/', AppointmentCreateView.as_view(), name='appointment-create'),
    path('appointment/<int:pk>/', AppointmentDetailView.as_view(), name='appointment-detail'),
    path('appointment/<int:pk>/update/', AppointmentUpdateView.as_view(), name='appointment-update'),
    path('appointment/<int:pk>/confirm/', AppointmentConfirmView.as_view(), name='appointment-confirm'),
    path('appointment/<int:pk>/complete/', AppointmentCompleteView.as_view(), name='appointment-complete'),
    path('appointment/<int:pk>/cancel/', AppointmentCancelView.as_view(), name='appointment-cancel'),
    path('appointment/pending/', PendingAppointmentsView.as_view(), name='appointment-pending'),
    path('appointment/upcoming/', UpcomingAppointmentsView.as_view(), name='appointment-upcoming'),
    

    path('consultations/', ConsultationListView.as_view(), name='consultation-list'),
    path('consultations/create/', ConsultationCreateView.as_view(), name='consultation-create'),
    path('consultations/<int:pk>/', ConsultationDetailView.as_view(), name='consultation-detail'),
    path('consultations/my-history/', ClientConsultationHistoryView.as_view(), name='client-consultation-history'),
    path('consultations/my-consultations/', VetConsultationHistoryView.as_view(), name='vet-consultation-history'),
]