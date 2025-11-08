from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView

from core.incident.models import Incident


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Dashboard'

        context['recent_incidents'] = Incident.objects.filter(
            is_active=True
        ).select_related(
            'incident_type',
            'incident_status',
            'reported_by_user'
        ).order_by('-reported_at')[:5]

        return context
