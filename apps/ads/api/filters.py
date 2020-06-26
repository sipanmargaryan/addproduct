from django_filters import rest_framework as filters

import ads.models

__all__ = (
    'MyAdsFilter',
)


class MyAdsFilter(filters.FilterSet):
    status = filters.CharFilter(field_name='status', method='status_filter', required=False)

    @staticmethod
    def status_filter(queryset, name, value):
        if value == 'inactive':
            return queryset.inactive()

        return queryset.active()

    class Meta:
        model = ads.models.Ad
        fields = ['status']
