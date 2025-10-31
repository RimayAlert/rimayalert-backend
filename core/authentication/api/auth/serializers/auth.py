from rest_framework import serializers

from core.authentication.models import User


class AuthTokenSerializerInput(serializers.ModelSerializer):
    username = serializers.CharField()
    password = serializers.CharField()

    class Meta:
        model = User
        fields = ['username', 'password']
