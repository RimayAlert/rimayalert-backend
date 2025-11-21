from django.urls import path, include

from core.incident.views.incident.incident import IncidentListView, IncidentDetailView, ResolveIncidentView

app_name = 'incident'

urlpatterns = [
    path('', IncidentListView.as_view(), name='incident_list'),
    path('<int:pk>/', IncidentDetailView.as_view(), name='incident_detail'),
    path('<int:pk>/resolve/', ResolveIncidentView.as_view(), name='resolve_incident'),
    #     API
    path('api/', include('core.incident.api.urls'))

]
