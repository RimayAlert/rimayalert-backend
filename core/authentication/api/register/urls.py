from django.urls import path

from core.authentication.api.register.views.fcm_token import UpdateFCMTokenApiView
from core.authentication.api.register.views.register import RegisterUserApiView

urlpatterns = [
    path('user', RegisterUserApiView.as_view(), name='api_register_user'),
    path('update_fcm_token', UpdateFCMTokenApiView.as_view(), name='api_update_fcm_token')
]
