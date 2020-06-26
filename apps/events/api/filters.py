from django_filters import rest_framework as filters

from django.db.models import Q
from django.utils import timezone

import events.models
from ads.filters import CustomFilter

__all__ = (
    'EventFilter',
)


class EventFilter(filters.FilterSet):
    q = filters.CharFilter(method='filter_keyword')
    status = filters.CharFilter(method='filter_status')
    date = filters.DateFilter(method='filter_date')
    category = CustomFilter(field_name='category__pk')

    class Meta:
        model = events.models.Event
        fields = ['category']

    @staticmethod
    def filter_status(queryset, name, value):
        if value == 'previous':
            return queryset.filter(end_date__lte=timezone.now())

        return queryset.filter(start_date__gte=timezone.now())

    @staticmethod
    def filter_date(queryset, name, value):
        return queryset.filter(start_date__lte=value, end_date__gte=value)

    @staticmethod
    def filter_keyword(queryset, name, value):
        if not value:
            return queryset

        return queryset.filter(Q(title__icontains=value) | Q(description__icontains=value))
