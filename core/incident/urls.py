from django.urls import path

from core.incident.views.incident.incident import IncidentListView, IncidentDetailView

app_name = 'incident'

urlpatterns = [
    path('', IncidentListView.as_view(), name='incident_list'),
    path('<int:pk>/', IncidentDetailView.as_view(), name='incident_detail'),
]