from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from django.conf import settings
from core.incident.models import Incident


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Dashboard'

        # Información del producto activo
        context['product_name'] = settings.PRODUCT_NAME
        context['product_description'] = settings.PRODUCT_DESCRIPTION

        context['recent_incidents'] = Incident.objects.filter(
            is_active=True
        ).select_related(
            'incident_type',
            'incident_status',
            'reported_by_user'
        ).order_by('-reported_at')[:5]

        # Verificar si stats está habilitado
        context['stats_enabled'] = settings.ENABLE_STATS

        if settings.ENABLE_STATS:
            from core.stats.models import UserStats
            try:
                user_stats = UserStats.objects.get(user=self.request.user)
                context['user_stats'] = user_stats
            except UserStats.DoesNotExist:
                context['user_stats'] = None

        return context