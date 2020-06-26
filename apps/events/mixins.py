from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db.models import Q
from django.utils import timezone

import events.models


class SearchMixin(object):

    def filter_queryset(self, queryset, params):
        if params['search']:
            queryset = queryset.filter(
                Q(title__icontains=params['search']) | Q(description__icontains=params['search'])
            )
        if params['category']:
            queryset = queryset.filter(category__pk=params['category'])
        if params['city']:
            queryset = queryset.filter(city__pk=params['city'])

        return queryset

    def filter_params(self, params):
        return dict(
            search=params.get('q', None),
            category=params.get('category', None),
            city=params.get('city', None),
        )


class EventDataMixin(object):
    def get_queryset(self, filter_by='upcoming'):
        filter_by = self.request.GET.get('filter_by', filter_by)

        manager = events.models.Event.objects
        if filter_by == 'upcoming':
            queryset = manager.filter(start_date__gte=timezone.now())
        else:
            queryset = manager.filter(end_date__lte=timezone.now())

        return queryset.select_related('city', 'category')

    def get_paginated_events(self, queryset, page_size=9):

        paginate_event = self.paginate_data(queryset, page_size)
        event_list = paginate_event.object_list

        return dict(
            events=event_list,
            paginate=paginate_event,
        )

    def paginate_data(self, queryset, paginate_by):
        page = self.request.GET.get('page', 1)
        paginator = Paginator(queryset, paginate_by)
        try:
            queryset = paginator.page(page)
        except PageNotAnInteger:
            queryset = paginator.page(paginate_by)
        except EmptyPage:
            queryset = paginator.page(paginator.num_pages)

        return queryset
