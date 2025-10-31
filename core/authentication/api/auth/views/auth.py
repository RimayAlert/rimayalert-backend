from django.db import transaction
from rest_framework import status
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.response import Response

from core.authentication.api.auth.features.auth import AuthenticationFeature
from core.authentication.api.auth.serializers.auth import AuthTokenSerializerInput


class CustomAuthTokenApiView(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        try:
            with transaction.atomic():
                serializer = AuthTokenSerializerInput(data=request.data)
                serializer.is_valid(raise_exception=True)

                username = serializer.validated_data['username']
                password = serializer.validated_data['password']

                token, result = AuthenticationFeature.login_user(username, password)
                if token is None:
                    return Response({'detail': result['message']}, status=result['code'])

                return Response({'message': result['message'],'token': token.key}, status=result['code'])

        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)
