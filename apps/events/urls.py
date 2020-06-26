from django.urls import path

from . import views

app_name = 'events'
urlpatterns = [
    path('event/<int:pk>/<str:slug>/', views.EventView.as_view(), name='event_detail'),
    path('upcoming-events/', views.EventsView.as_view(filter_by='upcoming'), name='upcoming_events'),
    path('previous-events/', views.EventsView.as_view(filter_by='previous'), name='previous_events'),
    path('events/', views.EventsListView.as_view(), name='event_list'),
]
