from django.shortcuts import redirect, render
from django.views.generic import TemplateView, FormView
from django.contrib import messages
from django.conf import settings
from django.urls import reverse_lazy

from config.mixins.permissions.permissions import PermissionMixin
from core.incident.models import Incident
from core.community.models import Community
from core.community.models.community_membership.community_membership import CommunityMembership
from core.authentication.models import UserProfile
from core.authentication.forms.user_profile.user_profile_form import UserProfileForm
from core.community.forms.community.community_form import CommunityForm


class DashboardView(PermissionMixin, TemplateView):
    permission_required = 'can_manage_community'
    template_name = 'dashboard/home/dashboard.html'

    def get(self, request, *args, **kwargs):
        # Check if user has profile
        has_profile = UserProfile.objects.filter(user=request.user).exists()
        if not has_profile:
            return redirect('dashboard:create_profile')
        
        # Check if any community exists
        has_community = Community.objects.exists()
        if not has_community:
            return redirect('dashboard:create_community')
        
        return super().get(request, *args, **kwargs)

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


class CreateUserProfileView(PermissionMixin, FormView):
    permission_required = 'can_manage_community'
    template_name = 'dashboard/profile/create_profile.html'
    form_class = UserProfileForm
    success_url = reverse_lazy('dashboard:dashboard')

    def dispatch(self, request, *args, **kwargs):
        if UserProfile.objects.filter(user=request.user).exists():
            return redirect('dashboard:dashboard')
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Completa tu Perfil'
        context['GOOGLE_MAPS_API_KEY'] = settings.GOOGLE_MAPS_API_KEY
        return context

    def form_valid(self, form):
        profile = form.save(commit=False)
        profile.user = self.request.user
        profile.save()
        messages.success(self.request, 'Perfil creado exitosamente.')
        return super().form_valid(form)


class CreateCommunityView(PermissionMixin, FormView):
    permission_required = 'can_manage_community'
    template_name = 'dashboard/community/create_community.html'
    form_class = CommunityForm
    success_url = reverse_lazy('dashboard:dashboard')

    def dispatch(self, request, *args, **kwargs):
        if Community.objects.exists():
            return redirect('dashboard:dashboard')
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Crear Comunidad'
        context['GOOGLE_MAPS_API_KEY'] = settings.GOOGLE_MAPS_API_KEY
        return context

    def form_valid(self, form):
        community = form.save()
        
        CommunityMembership.objects.create(
            user=self.request.user,
            community=community,
            role='admin',
            is_verified=True
        )
        
        messages.success(self.request, 'Comunidad creada exitosamente y has sido asignado como administrador.')
        return super().form_valid(form)
