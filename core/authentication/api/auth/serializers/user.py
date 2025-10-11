from rest_framework import serializers

from core.authentication.models import User


class AuthTokenSerializerInput(serializers.ModelSerializer):
    username = serializers.CharField()
    password = serializers.CharField()
    dni = serializers.CharField()
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    email = serializers.EmailField()

    class Meta:
        model = User
        fields = ['username', 'password', 'dni', 'first_name', 'last_name', 'email']
