from django.views.generic import ListView, DetailView
from django.shortcuts import get_object_or_404

from core.community.forms.community import SearchCommunityForm, SearchMemberForm
from core.community.models import Community
from core.community.models import CommunityMembership


class CommunityListView(ListView):
    model = Community
    template_name = "community/list/community_list.html"
    context_object_name = 'items'

    def get_queryset(self):
        queryset = super().get_queryset()

        form = SearchCommunityForm(self.request.GET)
        if form.is_valid():
            is_active = form.cleaned_data.get('is_active')
            if is_active is not None:
                queryset = queryset.filter(is_active=is_active)

            postal_code = form.cleaned_data.get('postal_code')
            if postal_code:
                queryset = queryset.filter(postal_code__icontains=postal_code)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_form'] = SearchCommunityForm(self.request.GET or None)
        return context


class CommunityDetailView(DetailView):
    model = Community
    template_name = "community/detail/community_detail.html"
    context_object_name = 'community'


class CommunityMemberListView(ListView):
    model = CommunityMembership
    template_name = "community/member_list/community_member_list.html"
    context_object_name = 'members'
    paginate_by = 20

    def get_queryset(self):
        self.community = get_object_or_404(Community, pk=self.kwargs['pk'])
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
        context['community'] = self.community
        context['search_form'] = SearchMemberForm(self.request.GET or None)
        return context
