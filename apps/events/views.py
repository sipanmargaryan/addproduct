from django.conf import settings
from django.views import generic

import core.models
import events.mixins
import events.models

__all__ = (
    'EventView',
    'EventsView',
    'EventsListView',
)


class EventView(generic.DetailView):
    model = events.models.Event
    template_name = 'events/event_detail.html'
    context_object_name = 'event'

    def get_context_data(self, **kwargs):
        context = super(EventView, self).get_context_data(**kwargs)
        context['google_api_key'] = settings.GOOGLE_API_KEY
        return context


class EventsView(
    events.mixins.EventDataMixin,
    events.mixins.SearchMixin,
    generic.TemplateView
):
    template_name = 'events/events.html'
    filter_by = 'upcoming'
    sort_by = '-start_date'

    def get_context_data(self, **kwargs):
        context = super(EventsView, self).get_context_data(**kwargs)
        context['filter_by'] = self.filter_by
        context['categories'] = events.models.Category.objects.order_by('name')
        context['cities'] = core.models.City.objects.order_by('name')

        data = self.get_events()
        context['events'] = data['events']
        context['paginate'] = data['paginate']

        return context

    def get_events(self):
        filter_by = self.request.GET.get('filter_by', self.filter_by)
        sort_by = self.request.GET.get('sort_by', self.sort_by)
        queryset = self.get_queryset(filter_by=filter_by).order_by(sort_by)

        queryset = self.filter_queryset(
            queryset,
            self.filter_params(self.request.GET)
        )

        return self.get_paginated_events(queryset=queryset)


class EventsListView(
    events.mixins.EventDataMixin,
    events.mixins.SearchMixin,
    generic.TemplateView
):
    template_name = 'events/includes/events.html'
    sort_by = '-start_date'

    def get_context_data(self, **kwargs):
        context = super(EventsListView, self).get_context_data(**kwargs)
        filter_by = self.request.GET.get('filter_by', 'upcoming')
        sort_by = self.request.GET.get('sort_by', self.sort_by)
        queryset = self.get_queryset(filter_by=filter_by).order_by(sort_by)

        queryset = self.filter_queryset(
            queryset,
            self.filter_params(self.request.GET)
        )

        data = self.get_paginated_events(queryset=queryset)
        context['events'] = data['events']
        context['paginate'] = data['paginate']

        return context
