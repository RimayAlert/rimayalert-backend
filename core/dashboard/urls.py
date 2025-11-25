from django.urls import path

from core.dashboard.views.dashboard.dashboard import DashboardView, CreateUserProfileView, CreateCommunityView

app_name = 'dashboard'

urlpatterns = [
    path('', DashboardView.as_view(), name='dashboard'),
    path('create-profile/', CreateUserProfileView.as_view(), name='create_profile'),
    path('create-community/', CreateCommunityView.as_view(), name='create_community'),
]
