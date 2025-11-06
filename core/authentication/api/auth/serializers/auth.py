from rest_framework import serializers

from core.authentication.models import User


class AuthTokenSerializerInput(serializers.ModelSerializer):
    username = serializers.CharField()
    password = serializers.CharField()

    class Meta:
        model = User
        fields = ['username', 'password']


class UserProfileDataSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = '__all__'

    def to_representation(self, instance):
        return instance.to_json_api()
