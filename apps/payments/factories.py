import factory
from factory.fuzzy import FuzzyFloat, FuzzyInteger

import ads.factories
import payments.models
import users.factories


class PaymentFactory(factory.DjangoModelFactory):
    cost = FuzzyFloat(8.5, 52.7)
    premium_days = FuzzyInteger(1, 7)
    ad = factory.SubFactory(ads.factories.AdFactory)
    user = factory.SubFactory(users.factories.UserFactory)

    class Meta:
        model = payments.models.Payment
