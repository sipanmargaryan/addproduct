from django.urls import path

from .views import *  # noqa

app_name = 'common_api'
urlpatterns = [
    path('services/', ServicesAPIView.as_view(), name='services'),
    path('cities/', CitiesAPIView.as_view(), name='cities'),
    path('service-categories/', CategoriesAPIView.as_view(), name='category'),
    path('living-in-kuwait/', LivingInKuwaitAPIView.as_view(), name='living'),
]
