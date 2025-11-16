from rest_framework import serializers


class UpdateFCMTokenSerializer(serializers.Serializer):
    fcm_token = serializers.CharField(required=True, max_length=255)
    device_id = serializers.CharField(required=False, allow_blank=True, max_length=255)
