import factory

import core.models


class CityFactory(factory.DjangoModelFactory):
    name = factory.Sequence(lambda n: 'city-{}'.format(n))

    class Meta:
        model = core.models.City
