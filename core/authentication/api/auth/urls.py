from django.urls import path

from core.authentication.api.auth.views.auth import CustomAuthTokenApiView

urlpatterns = [
    path('login', CustomAuthTokenApiView.as_view(), name='api_login'),
]
