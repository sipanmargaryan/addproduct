from django_filters import rest_framework as filters

from django.db.models import Q

import faq.models
from ads.filters import CustomFilter

__all__ = (
    'QuestionFilter',
)


class QuestionFilter(filters.FilterSet):
    q = filters.CharFilter(method='filter_keyword')
    status = filters.CharFilter(method='filter_status')
    category = CustomFilter(field_name='category__pk')

    class Meta:
        model = faq.models.Question
        fields = ['category']

    @staticmethod
    def filter_keyword(queryset, name, value):
        if not value:
            return queryset

        return queryset.filter(Q(title__icontains=value) | Q(description__icontains=value))

    @staticmethod
    def filter_status(queryset, name, value):
        if value == 'recent':
            return queryset.order_by('-created')

        return queryset
