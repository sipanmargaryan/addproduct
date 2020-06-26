from rest_framework import generics

import ads.models

from ..serializers import *  # noqa

__all__ = (
    'CarMakesAPIView',
    'CarModelsAPIView',
    'MobileBrandsAPIView',
    'MobileModelsAPIView',
)


class CarMakesAPIView(generics.ListAPIView):
    queryset = ads.models.CarMakeCategory.objects.order_by('name')
    serializer_class = CarMakeCategorySerializer


class CarModelsAPIView(generics.ListAPIView):
    queryset = ads.models.CarModelCategory.objects.all()
    serializer_class = CarModelCategorySerializer

    def get_queryset(self):
        return self.queryset.filter(make=self.kwargs['pk']).order_by('name')


class MobileBrandsAPIView(generics.ListAPIView):
    queryset = ads.models.MobileBrandCategory.objects.order_by('name')
    serializer_class = MobileBrandCategorySerializer


class MobileModelsAPIView(generics.ListAPIView):
    queryset = ads.models.MobileModelCategory.objects.all()
    serializer_class = MobileModelCategorySerializer

    def get_queryset(self):
        return self.queryset.filter(brand=self.kwargs['pk']).order_by('name')
