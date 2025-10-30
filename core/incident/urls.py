from django.urls import path

from core.incident.views.incident.incident import IncidentListView

app_name = 'incident'

urlpatterns = [
    path('', IncidentListView.as_view(), name='incident_list'),
]