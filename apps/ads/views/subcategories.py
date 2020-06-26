from django.http import JsonResponse
from django.views import generic

import ads.models

__all__ = (
    'CarModelView',
    'MobileModelView',
)


class CarModelView(generic.View):
    # noinspection PyMethodMayBeStatic, PyUnusedLocal
    def get(self, request, *args, **kwargs):
        make = request.GET.get('make')
        models = ads.models.CarModelCategory.objects.filter(make=make).values('pk', 'name').order_by('name')

        return JsonResponse({'models': list(models)})


class MobileModelView(generic.View):
    # noinspection PyMethodMayBeStatic, PyUnusedLocal
    def get(self, request, *args, **kwargs):
        brand = request.GET.get('brand')
        models = ads.models.MobileModelCategory.objects.filter(brand=brand).values('pk', 'name').order_by('name')

        return JsonResponse({'models': list(models)})
