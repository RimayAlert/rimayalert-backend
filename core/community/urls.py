from django.urls import path

from core.community.views.community.community import CommunityListView, CommunityDetailView

app_name = 'community'

urlpatterns = [
    path('', CommunityListView.as_view(), name='community_list'),
    path('<int:pk>/', CommunityDetailView.as_view(), name='community_detail'),
]

