from django_filters import rest_framework as filters
from rest_framework import generics

import events.models
from events.api.filters import EventFilter

from .serializers import *  # noqa

__all__ = (
    'EventsAPIView',
    'EventDetailAPIView',
    'CategoriesAPIView',
)


class EventsAPIView(generics.ListAPIView):
    queryset = events.models.Event.objects.all()
    serializer_class = EventsSerializer

    filter_backends = (filters.DjangoFilterBackend,)
    filter_class = EventFilter


class EventDetailAPIView(generics.RetrieveAPIView):
    queryset = events.models.Event.objects.all()
    serializer_class = EventsSerializer

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)


class CategoriesAPIView(generics.ListAPIView):
    queryset = events.models.Category.objects.all()
    serializer_class = CategorySerializer
