from django.urls import path, include

urlpatterns = [
    path('register/', include('core.authentication.api.register.urls')),
]
