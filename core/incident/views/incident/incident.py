from django.views.generic import ListView, DetailView

from core.incident.models import Incident
from core.incident.forms import SearchIncidentForm


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

        form = SearchIncidentForm(self.request.GET)
        if form.is_valid():
            incident_type = form.cleaned_data.get('type')
            if incident_type:
                queryset = queryset.filter(incident_type=incident_type)

            incident_status = form.cleaned_data.get('status')
            if incident_status:
                queryset = queryset.filter(incident_status=incident_status)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_form'] = SearchIncidentForm(self.request.GET or None)
        return context


class IncidentDetailView(DetailView):
    model = Incident
    template_name = "incident/detail/incident_detail.html"
    context_object_name = 'incident'

    def get_queryset(self):
        return super().get_queryset().select_related(
            'incident_type',
            'incident_status',
            'reported_by_user',
            'community',
        )
