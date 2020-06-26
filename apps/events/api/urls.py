from django.urls import path

from .views import *  # noqa

app_name = 'events_api'
urlpatterns = [
    path('events/', EventsAPIView.as_view(), name='events'),
    path('event/<int:pk>/', EventDetailAPIView.as_view(), name='event_detail'),
    path('categories/', CategoriesAPIView.as_view(), name='category'),
]
