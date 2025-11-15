from django.conf import settings
from django.views.generic import ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages

from core.community.forms.community import SearchMemberForm
from core.community.models import Community
from core.community.models import CommunityMembership


class CommunityDetailView(LoginRequiredMixin, DetailView):
    model = Community
    template_name = "community/detail/community_detail.html"
    context_object_name = 'community'

    def get_object(self, queryset=None):
        membership = CommunityMembership.objects.filter(
            user=self.request.user
        ).select_related('community').first()

        if membership:
            return membership.community
        return None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['GOOGLE_MAPS_API_KEY'] = settings.GOOGLE_MAPS_API_KEY
        return context


class CommunityMemberListView(LoginRequiredMixin, ListView):
    model = CommunityMembership
    template_name = "community/member_list/community_member_list.html"
    context_object_name = 'items'
    paginate_by = 20

    def get_queryset(self):
        membership = CommunityMembership.objects.filter(
            user=self.request.user
        ).select_related('community').first()

        if not membership:
            return CommunityMembership.objects.none()

        self.community = membership.community
        queryset = CommunityMembership.objects.filter(
            community=self.community
        ).select_related('user', 'community').order_by('-joined_at')

        form = SearchMemberForm(self.request.GET)
        if form.is_valid():
            role = form.cleaned_data.get('role')
            if role:
                queryset = queryset.filter(role=role)

            is_verified = form.cleaned_data.get('is_verified')
            if is_verified is not None:
                queryset = queryset.filter(is_verified=is_verified)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['community'] = getattr(self, 'community', None)
        context['search_form'] = SearchMemberForm(self.request.GET or None)
        return context


class VerifyMemberView(LoginRequiredMixin, View):

    def post(self, request, pk):
        membership = get_object_or_404(CommunityMembership, pk=pk)

        user_membership = CommunityMembership.objects.filter(
            user=request.user,
            community=membership.community
        ).first()

        if not user_membership:
            messages.error(request, "No tienes acceso a esta comunidad.")
            return redirect('dashboard:dashboard')

        if user_membership.role not in ['admin', 'moderator']:
            messages.error(request, "No tienes permisos para verificar miembros.")
            return redirect('community:community_members')

        membership.is_verified = not membership.is_verified
        membership.save()

        if membership.is_verified:
            messages.success(
                request,
                f"<strong>{membership.user.username}</strong> ha sido verificado exitosamente."
            )
        else:
            messages.warning(
                request,
                f"Se ha removido la verificación de <strong>{membership.user.username}</strong>."
            )

        return redirect('community:community_members')
