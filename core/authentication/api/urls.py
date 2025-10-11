from django.urls import path, include

urlpatterns = [
    path('auth', include('core.authentication.api.auth.urls')),
]
