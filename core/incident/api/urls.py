from django.urls import path, include

urlpatterns = [
    path('alert/', include('core.incident.api.incident.urls')),
]
