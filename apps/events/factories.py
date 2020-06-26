import factory
from factory.fuzzy import FuzzyDateTime, FuzzyDecimal, FuzzyText

from django.utils import timezone

import core.factories
import events.models

__all_ = (
    'CategoryFactory',
    'EventFactory',
)


class CategoryFactory(factory.DjangoModelFactory):
    name = factory.Sequence(lambda n: 'category-{}'.format(n))

    class Meta:
        model = events.models.Category


class EventFactory(factory.DjangoModelFactory):

    title = factory.Sequence(lambda n: 'title-{}'.format(n))
    address = FuzzyText(length=200)
    description = FuzzyText(length=200)
    price = FuzzyText(length=30)
    registration_url = 'http://example.com/'
    latitude = FuzzyDecimal(1, 100, 8)
    longitude = FuzzyDecimal(1, 100, 8)
    start_date = FuzzyDateTime(timezone.now())
    end_date = FuzzyDateTime(
        timezone.now(),
        timezone.now() + timezone.timedelta(days=5, hours=5)
    )

    category = factory.SubFactory(CategoryFactory)
    city = factory.SubFactory(core.factories.CityFactory)

    class Meta:
        model = events.models.Event
