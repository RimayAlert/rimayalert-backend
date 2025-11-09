from django.urls import path

from core.incident.api.incident.views.incident import RegisterIncidentApiView
from core.incident.api.incident.views.incident_list import ListIncidentApiView

urlpatterns = [
    path('create', RegisterIncidentApiView.as_view(), name='api_register_incident'),
    path('list', ListIncidentApiView.as_view(), name='api_list_incident'),
]
