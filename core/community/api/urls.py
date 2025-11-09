from django.urls import path, include

urlpatterns = [
    path('community/', include('core.community.api.community.urls')),
]
