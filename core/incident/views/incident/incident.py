from django.views.generic import ListView

from core.incident.models import Incident


class IncidentListView(ListView):
    model = Incident
    template_name = "incident/list/incident_list.html"
    context_object_name = 'items'

    def get_queryset(self):
        queryset = super().get_queryset().prefetch_related(
            'incident_type',
            'incident_status',
            'reported_by_user',
        )
        incident_type = self.request.GET.get('type')
        if incident_type:
            queryset = queryset.filter(incident_type__name=incident_type)
        incident_status = self.request.GET.get('status')
        if incident_status:
            queryset = queryset.filter(incident_status__name=incident_status)
        return queryset
