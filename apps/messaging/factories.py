import factory

import ads.factories
import messaging.models
import users.factories


class ThreadFactory(factory.DjangoModelFactory):
    ad = factory.SubFactory(ads.factories.AdFactory)

    class Meta:
        model = messaging.models.Thread

    @factory.post_generation
    def users(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            for user in extracted:
                self.users.add(user)


class MessageFactory(factory.DjangoModelFactory):
    message = factory.Sequence(lambda n: 'message-{}'.format(n))

    thread = factory.SubFactory(ThreadFactory)
    sender = factory.SubFactory(users.factories.UserFactory)

    class Meta:
        model = messaging.models.Message
