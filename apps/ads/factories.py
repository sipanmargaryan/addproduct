import random

import factory

import ads.models
import users.factories


class CategoryFactory(factory.DjangoModelFactory):
    class Meta:
        model = ads.models.Category


class AdFactory(factory.DjangoModelFactory):
    price = random.choice(range(100, 10000, 100))

    user = factory.SubFactory(users.factories.UserFactory)

    class Meta:
        model = ads.models.Ad


class FavoriteAdFactory(factory.DjangoModelFactory):
    ad = factory.SubFactory(AdFactory)
    user = factory.SubFactory(users.factories.UserFactory)

    class Meta:
        model = ads.models.FavoriteAd


class AdImageFactory(factory.DjangoModelFactory):
    ad = factory.SubFactory(AdFactory)

    class Meta:
        model = ads.models.AdImage


class AdReviewFactory(factory.DjangoModelFactory):
    ad = factory.SubFactory(AdFactory)
    user = factory.SubFactory(users.factories.UserFactory)

    class Meta:
        model = ads.models.AdReview
