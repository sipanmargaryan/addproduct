import json

import pytest

from django.db import transaction

from messaging.factories import ThreadFactory
from users.factories import UserFactory


@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True)
async def test_consumer(communicator, monkeypatch):
    with transaction.atomic():
        user = UserFactory()
        thread = ThreadFactory(users=(user, UserFactory()))

    # noinspection PyUnusedLocal
    def retrieve_user(self):
        return user
    monkeypatch.setattr('messaging.consumers.MessageConsumer.retrieve_user', retrieve_user)

    communicator = await communicator(thread.chat_url)
    await communicator.send_json_to({'message': 'message'})
    response = await communicator.receive_from()
    response = json.loads(response)
    assert response['message'] == 'message'
    await communicator.disconnect()
