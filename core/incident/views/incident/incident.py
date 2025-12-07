from django.conf import settings
from django.views.generic import ListView, DetailView, View
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages

from core.incident.models import Incident, IncidentStatus
from core.stats.models import UserStats
from core.incident.forms import SearchIncidentForm
from config.mixins.permissions.permissions import PermissionMixin

class IncidentListView(PermissionMixin, ListView):
    permission_required = 'can_manage_community'
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


class IncidentDetailView(PermissionMixin, DetailView):
    permission_required = 'can_manage_community'
    model = Incident
    template_name = "incident/detail/incident_detail.html"
    context_object_name = 'incident'

    def get_queryset(self):
        return super().get_queryset().select_related(
            'incident_type',
            'incident_status',
            'reported_by_user',
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['GOOGLE_MAPS_API_KEY'] = settings.GOOGLE_MAPS_API_KEY
        return context


class ResolveIncidentView(PermissionMixin, View):
    permission_required = 'can_manage_community'

    def post(self, request, *args, **kwargs):
        incident = get_object_or_404(Incident, pk=kwargs.get('pk'))
        
        try:
            resolved_status = IncidentStatus.objects.get(code='003')
        except IncidentStatus.DoesNotExist:
            resolved_status = IncidentStatus.objects.get(name='Resuelto')
            
        incident.incident_status = resolved_status
        stats, _ = UserStats.objects.get_or_create(user=incident.reported_by_user)
        stats.total_alerts_pending = max(0, stats.total_alerts_pending - 1)
        stats.total_alerts_resolved += 1
        stats.save()
        incident.save()
        
        messages.success(request, 'Incidente marcado como resuelto exitosamente.')
        return redirect('incident:incident_list')
