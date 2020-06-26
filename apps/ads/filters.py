import django_filters

from django.db.models import Q
from django.forms.widgets import TextInput
from django.utils.translation import gettext as _

import ads.models

__all__ = (
    'CustomFilter',
    'AdFilter',
)


class CustomFilter(django_filters.Filter):
    def filter(self, qs, value):
        if value:
            value_list = value.split(',')
            filter_data = {
                f'{self.field_name}__in': value_list
            }
            qs = qs.filter(**filter_data)
        return qs


class AdFilter(django_filters.FilterSet):
    q = django_filters.CharFilter(
        method='filter_keyword',
        widget=TextInput(attrs={'placeholder': _('What are you looking for ?')}),
    )
    price_min = django_filters.NumberFilter(field_name='price', lookup_expr='gte')
    price_max = django_filters.NumberFilter(field_name='price', lookup_expr='lte')
    seller_type = django_filters.CharFilter(method='filter_seller_type')
    city = django_filters.CharFilter(method='filter_city')
    state = django_filters.CharFilter(method='filter_state')
    category = CustomFilter(field_name='category__name')

    class Meta:
        model = ads.models.Ad
        fields = ['seller_type', 'state']

    @staticmethod
    def filter_keyword(queryset, name, value):
        if not value:
            return queryset

        return queryset.filter(Q(title__icontains=value) | Q(description__icontains=value))

    @staticmethod
    def filter_seller_type(queryset, name, value):
        selected_type = dict()
        if value == 'private':
            selected_type['is_seller_private'] = True
        elif value == 'business':
            selected_type['is_seller_private'] = False
        return queryset.filter(**selected_type)

    @staticmethod
    def filter_state(queryset, name, value):
        ad_state = dict()
        if value in ['new', 'used']:
            ad_state['state'] = value
        return queryset.filter(**ad_state)

    @staticmethod
    def filter_city(queryset, name, value):
        return queryset.filter(city__name=value)
