from django.urls import path, include

from core.community.views.community.community import CommunityListView, CommunityDetailView, CommunityMemberListView

app_name = 'community'

urlpatterns = [
    path('', CommunityListView.as_view(), name='community_list'),
    path('<int:pk>/', CommunityDetailView.as_view(), name='community_detail'),
    path('<int:pk>/members/', CommunityMemberListView.as_view(), name='community_members'),

    #     API
    path('api/', include('core.community.api.urls')),
]
