import logging

from django.db import transaction
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from core.authentication.api.auth.features.user import AuthApiUser
from core.authentication.api.auth.serializers.user import AuthTokenSerializerInput

logger = logging.getLogger(__name__)


class CustomAuthTokenApiView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        try:
            with transaction.atomic():
                serializer = AuthTokenSerializerInput(data=request.data)
                if serializer.is_valid(raise_exception=True):
                    auth_user = AuthApiUser(self.request)
                    result = auth_user.login(serializer.validated_data)
                    token = result['token']
                    return Response({'token': token}, status.HTTP_200_OK)
        except Exception as e:
            logger.error(str(e))
            return Response({'detail': 'Internal server error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)