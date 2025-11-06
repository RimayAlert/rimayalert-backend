from django.urls import path, include

from core.incident.views.incident.incident import IncidentListView, IncidentDetailView

app_name = 'incident'

urlpatterns = [
    path('', IncidentListView.as_view(), name='incident_list'),
    path('<int:pk>/', IncidentDetailView.as_view(), name='incident_detail'),
    #     API
    path('api/', include('core.incident.api.urls'))

]
