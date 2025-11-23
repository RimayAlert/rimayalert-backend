from rest_framework import serializers

from core.incident.models import Incident


class MapIncidentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Incident
        fields = '__all__'

    def to_representation(self, instance):
        return instance.to_json_map()
