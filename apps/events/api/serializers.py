from rest_framework import serializers

import events.models

__all__ = (
    'CategorySerializer',
    'EventsSerializer',
)


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = events.models.Category
        fields = ('pk', 'name')


class EventsSerializer(serializers.ModelSerializer):
    category = CategorySerializer()

    class Meta:
        model = events.models.Event
        fields = (
            'pk',
            'category',
            'title',
            'address',
            'description',
            'image',
            'price',
            'registration_url',
            'latitude',
            'longitude',
            'start_date',
            'end_date',
        )
