import logging

from django.db import transaction, IntegrityError
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from core.authentication.api.register.feature.FCM_token import RegisterFCMTokenFeature
from core.authentication.api.register.feature.register import RegisterUserProfileFeature
from core.authentication.api.register.serializers.register import RegisterUserSerializerInput

logger = logging.getLogger(__name__)


class RegisterUserApiView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def map_data_user(self, request_data):
        user_data = {
            "username": request_data.get("username"),
            "password": request_data.get("password"),
            "dni": request_data.get("dni"),
            "first_name": request_data.get("firstName"),
            "last_name": request_data.get("lastName"),
            "email": request_data.get("email")
        }
        return user_data

    def map_data_profile(self, request_data):
        return {
            "displayName": request_data.get("displayName"),
            "latitude": request_data.get("latitude"),
            "longitude": request_data.get("longitude"),
        }

    def map_data_token_fcm(self, request_data):
        return {
            "token": request_data.get("fcmToken"),
            "deviceId": request_data.get("deviceId")
        }

    def post(self, request, *args, **kwargs):
        try:
            with transaction.atomic():
                data_user_serializer = self.map_data_user(request.data)
                serializer = RegisterUserSerializerInput(data=data_user_serializer)
                serializer.is_valid(raise_exception=True)
                user = serializer.save()
                profile_data = self.map_data_profile(request.data)
                feature = RegisterUserProfileFeature()
                feature.create_user_profile(user, profile_data)

                fcm_data = self.map_data_token_fcm(request.data)
                if fcm_data.get("token"):
                    fcm_feature = RegisterFCMTokenFeature()
                    fcm_feature.register_or_update_token(user, fcm_data)

                return Response({"message": "User registered successfully"},
                                status=status.HTTP_201_CREATED)
        except ValidationError as ve:
            return Response({'errors': ve.detail}, status=status.HTTP_400_BAD_REQUEST)
        except IntegrityError as ie:
            return Response({'errors': 'User with this information already exists'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(str(e))
            return Response({'detail': 'Internal server error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
