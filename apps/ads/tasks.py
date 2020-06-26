import requests
from celery import task

from django.apps import apps
from django.conf import settings
from django.core.cache import cache
from django.utils import timezone

import ads.filters
import ads.utils


@task.task
def featured():
    ad_model = apps.get_model('ads', 'Ad')
    ad_model.objects.filter(premium_until__lte=timezone.now()).update(premium_until=None)


@task.task
def currency():
    url = f'http://data.fixer.io/api/latest?access_key={settings.FIXER_KEY}&symbols=USD,KWD'

    response = requests.get(url).json()

    rate = float(response['rates']['USD']) / float(response['rates']['KWD'])

    cache.set('kwd_usd_rate', rate)


@task.task
def notify_me():
    ad_model = apps.get_model('ads', 'Ad')
    saved_search_model = apps.get_model('ads', 'SavedSearch')
    _30_before = timezone.now() - timezone.timedelta(minutes=30)
    for search in saved_search_model.objects.all():
        queryset = (
            ad_model
            .objects
            .active()
            .filter(created__gte=_30_before)
            .exclude(user=search.user)
        )
        data = {k: v for k, v in search.data.items() if v}

        if 'categories' in data:
            del data['categories']
            data['category'] = ','.join(search.data.get('categories'))

        filter_data = ads.filters.AdFilter(data=data, queryset=queryset)

        count = filter_data.qs.count()
        if count:
            ads.utils.send_notify_me(
                search.user,
                context={
                    'search_url': search.search_url,
                    'search_count': count,
                }
            )

            search.last_notified = timezone.now()
            search.save()
