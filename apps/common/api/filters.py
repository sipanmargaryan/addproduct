from django_filters import rest_framework as filters

import common.models
from ads.filters import CustomFilter

__all__ = (
    'ServiceFilter',
)


class ServiceFilter(filters.FilterSet):
    q = filters.CharFilter(method='filter_keyword')
    category = CustomFilter(field_name='category__pk')

    class Meta:
        model = common.models.Service
        fields = ['category']

    @staticmethod
    def filter_keyword(queryset, name, value):
        if not value:
            return queryset

        return queryset.filter(name__icontains=value)
