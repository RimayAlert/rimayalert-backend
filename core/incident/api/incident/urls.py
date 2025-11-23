from django.urls import path

from core.incident.api.incident.views.incident import RegisterIncidentApiView
from core.incident.api.incident.views.incident_list import ListIncidentApiView
from core.incident.api.incident.views.map_incident import MapIncidentsApiView

urlpatterns = [
    path('create', RegisterIncidentApiView.as_view(), name='api_register_incident'),
    path('list', ListIncidentApiView.as_view(), name='api_list_incident'),
    path("detail", MapIncidentsApiView.as_view(), name="api_map_incidents")
]
