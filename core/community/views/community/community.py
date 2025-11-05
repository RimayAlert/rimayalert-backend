from django.views.generic import ListView, DetailView

from core.community.forms.community import SearchCommunityForm
from core.community.models import Community


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

