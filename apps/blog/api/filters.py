from django_filters import rest_framework as filters

from django.db.models import Q

import blog.models
from ads.filters import CustomFilter

__all__ = (
    'ArticlesFilter',
)


class ArticlesFilter(filters.FilterSet):
    q = filters.CharFilter(method='filter_keyword')
    order_by = filters.CharFilter(method='filter_date')
    category = CustomFilter(field_name='category__pk')

    class Meta:
        model = blog.models.Article
        fields = ['category']

    @staticmethod
    def filter_date(queryset, name, value):
        if value == 'popular':
            return queryset.order_by('-hit_count')

        return queryset

    @staticmethod
    def filter_keyword(queryset, name, value):
        if not value:
            return queryset

        return queryset.filter(Q(title__icontains=value) | Q(description__icontains=value))
