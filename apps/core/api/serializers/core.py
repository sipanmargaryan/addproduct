from rest_framework import serializers

import core.models

__all__ = (
    'CitySerializer',
)


class CitySerializer(serializers.ModelSerializer):
    class Meta:
        model = core.models.City
        fields = (
            'pk',
            'name',
        )
