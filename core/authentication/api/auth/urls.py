from django.urls import path

from core.authentication.api.auth.views.auth import CustomAuthTokenApiView

urlpatterns = [
    path('-token', CustomAuthTokenApiView.as_view(), name='api_token_auth'),
]
