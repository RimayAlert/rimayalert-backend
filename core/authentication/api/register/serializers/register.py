from rest_framework import serializers

from core.authentication.models import User


class RegisterUserSerializerInput(serializers.ModelSerializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)
    dni = serializers.CharField()
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    email = serializers.EmailField()

    class Meta:
        model = User
        fields = ['username', 'password', 'dni', 'first_name', 'last_name', 'email']

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user
