from django.urls import path

from core.stats.api.user_stats.views.user_stats import ListStatsApiView

urlpatterns = [
    path('list', ListStatsApiView.as_view(), name='api_list_user_stats'),
]
