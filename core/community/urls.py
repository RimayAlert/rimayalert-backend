from django.urls import path, include

from core.community.views.community.community import (
    CommunityDetailView,
    CommunityMemberListView,
    VerifyMemberView
)

app_name = 'community'

urlpatterns = [
    path('', CommunityDetailView.as_view(), name='community_detail'),
    path('members/', CommunityMemberListView.as_view(), name='community_members'),
    path('members/<int:pk>/verify/', VerifyMemberView.as_view(), name='verify_member'),

    #     API
    path('api/', include('core.community.api.urls')),
]
