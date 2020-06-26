import factory

from django.utils import timezone

import common.models


class ArticleFactory(factory.DjangoModelFactory):
    title = factory.Sequence(lambda n: 'help text title-{}'.format(n))
    description = factory.Sequence(lambda n: 'help text description-{}'.format(n))

    class Meta:
        model = common.models.Article


class CategoryFactory(factory.DjangoModelFactory):
    name = factory.Sequence(lambda n: 'category-{}'.format(n))

    class Meta:
        model = common.models.Category


class ServiceFactory(factory.DjangoModelFactory):
    opening_time = factory.lazy_attribute(lambda x: timezone.now())
    closing_time = factory.lazy_attribute(lambda x: timezone.now())

    category = factory.SubFactory(CategoryFactory)

    class Meta:
        model = common.models.Service
