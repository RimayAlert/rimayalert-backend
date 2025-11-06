import logging

from django.db import transaction
from rest_framework import status
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from core.authentication.api.auth.features.auth import AuthenticationFeature
from core.authentication.api.auth.serializers.auth import AuthTokenSerializerInput, UserProfileDataSerializer

logger = logging.getLogger(__name__)

class CustomAuthTokenApiView(ObtainAuthToken):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        try:
            with transaction.atomic():
                serializer = AuthTokenSerializerInput(data=request.data)
                serializer.is_valid(raise_exception=True)
                username = serializer.validated_data['username']
                password = serializer.validated_data['password']
                token, user, result = AuthenticationFeature.login_user(username, password)
                logger.info(result)
                if token is None:
                    return Response({'detail': result['message']}, status=result['code'])
                user_data = UserProfileDataSerializer(user).data
                response_data = {
                    'message': result['message'],
                    'token': token.key,
                    'user': user_data
                }
                logger.info(response_data)
                return Response(response_data, status=result['code'])

        except Exception as e:
            logger.error(str(e))
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)
