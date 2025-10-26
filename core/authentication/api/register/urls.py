from django.urls import path

from core.authentication.api.register.views.register import RegisterUserApiView

urlpatterns = [
    path('user', RegisterUserApiView.as_view(), name='api_register_user'),
]
