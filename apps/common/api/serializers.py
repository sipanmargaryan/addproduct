from rest_framework import serializers

import common.models

__all__ = (
    'CategorySerializer',
    'ServicesSerializer',
)


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = common.models.Category
        fields = ('pk', 'name')


class ServicesSerializer(serializers.ModelSerializer):
    category = CategorySerializer()

    class Meta:
        model = common.models.Service
        fields = (
            'pk',
            'name',
            'opening_time',
            'closing_time',
            'cover',
            'address',
            'category',
        )
