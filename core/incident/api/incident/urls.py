from django.urls import path, include

from core.incident.api.incident.views.incident import RegisterIncidentApiView

urlpatterns = [
    path('create', RegisterIncidentApiView.as_view(), name='api_register_incident'),
]
