from django.urls import path

from core.authentication.api.auth.views.auth import CustomAuthTokenApiView

urlpatterns = [
    path('user', CustomAuthTokenApiView.as_view(), name='api_auth_user'),
]
