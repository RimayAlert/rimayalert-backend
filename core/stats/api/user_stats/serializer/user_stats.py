from rest_framework import serializers

from core.stats.models import UserStats


class StatsListSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserStats
        fields = '__all__'

    def to_representation(self, instance):
        return instance.to_json_api()
