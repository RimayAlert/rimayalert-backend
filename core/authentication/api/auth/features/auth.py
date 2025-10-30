from django.contrib.auth import authenticate
from rest_framework import status
from rest_framework.authtoken.models import Token


class AuthenticationFeature:
    @staticmethod
    def login_user(username: str, password: str):
        user = authenticate(username=username, password=password)
        if user is None:
            return None, {'message': 'Credenciales inválidas', 'code': status.HTTP_400_BAD_REQUEST}

        token, created = Token.objects.get_or_create(user=user)
        return token, {'message': 'Inicio de sesión exitoso', 'code': status.HTTP_200_OK}
