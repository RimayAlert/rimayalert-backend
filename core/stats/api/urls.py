from django.urls import path, include

urlpatterns = [
    path('user-stats/', include('core.stats.api.user_stats.urls')),
]
