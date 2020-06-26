import pytest

from django.urls import reverse
from django.utils import timezone

import core.factories
import events.factories
import events.models


@pytest.mark.django_db
def test_event(client, image_file):
    event = events.factories.EventFactory(image=image_file())
    response = client.get(reverse('events:event_detail', kwargs={'pk': event.pk, 'slug': event.slug}))
    detail_event = response.context['event']

    assert response.status_code == 200
    assert event.pk == detail_event.pk


@pytest.mark.django_db
def test_event_invalid(client):
    response = client.get(reverse('events:event_detail', kwargs={'pk': 1, 'slug': 'event_slug_example'}))
    assert response.status_code == 404


@pytest.mark.django_db
def test_event_list(client, image_file):
    paginate_by = 9
    event_count = 30

    events.factories.EventFactory.create_batch(
        event_count, start_date=timezone.now() + timezone.timedelta(days=1), image=image_file()
    )
    response = client.get(reverse('events:event_list'))

    assert response.status_code == 200
    assert len(response.context['events']) == paginate_by

    events.factories.EventFactory(
        title='event', description='event description',
        start_date=timezone.now() + timezone.timedelta(days=1), image=image_file(),
    )
    payload = {'q': 'event'}

    response = client.get(reverse('events:event_list'), payload)

    assert response.status_code == 200
    assert len(response.context['events']) == 1


@pytest.mark.django_db
def test_event_list_category_filter(client, image_file):
    paginate_by = 9
    event_count = 30

    category = events.factories.CategoryFactory()
    events.factories.EventFactory.create_batch(
        event_count, category=category, image=image_file(),
        start_date=timezone.now() + timezone.timedelta(days=1),
    )
    payload = {'category': category.pk}

    response = client.get(reverse('events:event_list'), payload)

    assert response.status_code == 200
    assert len(response.context['events']) == paginate_by
    assert all([event.category.name == category.name for event in response.context['events']])


@pytest.mark.django_db
def test_event_list_city_filter(client, image_file):
    city = core.factories.CityFactory()
    events.factories.EventFactory(
        city=city, image=image_file(),
        start_date=timezone.now() + timezone.timedelta(days=1),
    )
    payload = {'city': city.pk}

    response = client.get(reverse('events:event_list'), payload)

    assert response.status_code == 200
    assert len(response.context['events']) == 1
    assert all([event.city.name == city.name for event in response.context['events']])


@pytest.mark.django_db
def test_events_view(client, image_file):
    for category in events.factories.CategoryFactory.create_batch(10):
        events.factories.EventFactory(
            start_date=timezone.now() + timezone.timedelta(days=1),
            image=image_file(),
            category=category,
        )

    response = client.get(reverse('events:upcoming_events'))

    assert response.status_code == 200
    assert len(response.context['events']) == 9
    assert len(response.context['categories']) == 10
