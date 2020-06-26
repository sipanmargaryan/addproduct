from django_filters import rest_framework as filters
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.response import Response

import common.models
import core.models
from blog.models import Article
from common.api.filters import ServiceFilter
from core.api.serializers import CitySerializer
from events.models import Event
from faq.models import Question

from .serializers import *  # noqa

__all__ = (
    'ServicesAPIView',
    'CategoriesAPIView',
    'LivingInKuwaitAPIView',
    'CitiesAPIView',
)


class ServicesAPIView(ListAPIView):
    queryset = common.models.Service.objects.all()
    serializer_class = ServicesSerializer

    filter_backends = (filters.DjangoFilterBackend,)
    filter_class = ServiceFilter


class CategoriesAPIView(ListAPIView):
    queryset = common.models.Category.objects.all()
    serializer_class = CategorySerializer


class LivingInKuwaitAPIView(RetrieveAPIView):

    def get(self, request, *args, **kwargs):
        news = Article.objects.count()
        events = Event.objects.count()
        faqs = Question.objects.count()
        services = common.models.Service.objects.count()
        return Response({
            'news': news,
            'events': events,
            'faqs': faqs,
            'services': services,
        })


class CitiesAPIView(ListAPIView):
    queryset = core.models.City.objects.all()
    serializer_class = CitySerializer
