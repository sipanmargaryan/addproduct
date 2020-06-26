import pytest

from django.apps import apps
from django.urls import reverse

import ads.factories
import messaging.factories
import users.factories


@pytest.mark.django_db
def test_inbox(logged_in):
    user = users.factories.UserFactory()
    thread = messaging.factories.ThreadFactory(users=(logged_in.user, user))
    messaging.factories.MessageFactory(thread=thread)
    response = logged_in.client.get(reverse('messaging:inbox'))
    assert response.status_code == 200
    assert len(response.context['threads']) == 1


@pytest.mark.django_db
def test_inbox_detail(logged_in):
    user = users.factories.UserFactory()
    thread = messaging.factories.ThreadFactory(users=(logged_in.user, user))
    messaging.factories.MessageFactory.create_batch(10, thread=thread, sender=logged_in.user)
    response = logged_in.client.get(reverse('messaging:inbox_detail', kwargs={'pk': thread.pk}))
    assert response.status_code == 200
    assert response.context['thread'].ad == thread.ad
    assert len(response.context['thread'].messages) == 10


@pytest.mark.django_db
def test_inbox_detail_invalid(logged_in):
    response = logged_in.client.get(reverse('messaging:inbox_detail', kwargs={'pk': 99}))
    assert response.status_code == 404


@pytest.mark.django_db
def test_block_thread(logged_in):
    user = users.factories.UserFactory()
    thread = messaging.factories.ThreadFactory(users=(logged_in.user, user))

    payload = {'thread_id': thread.pk}
    response = logged_in.client.post(reverse('messaging:block_thread'), payload)
    assert response.status_code == 204
    thread.refresh_from_db()

    assert thread.blocked


@pytest.mark.django_db
def test_block_thread_invalid(logged_in):
    user = users.factories.UserFactory()
    another_user = users.factories.UserFactory()
    thread = messaging.factories.ThreadFactory(users=(another_user, user))

    payload = {'thread_id': thread.pk}
    response = logged_in.client.post(reverse('messaging:block_thread'), payload)
    assert response.status_code == 404
    thread.refresh_from_db()

    assert not thread.blocked


@pytest.mark.django_db
def test_send_message_view(logged_in):
    user = users.factories.UserFactory()
    ad = ads.factories.AdFactory(user=user)

    payload = {'ad_id': ad.pk, 'message': 'Hello!'}
    response = logged_in.client.post(reverse('messaging:send_message'), payload)

    assert response.status_code == 302

    thread = apps.get_model('messaging', 'Thread').objects.get(ad=ad.pk, users=logged_in.user)
    message = apps.get_model('messaging', 'Message').objects.filter(thread=thread.pk).last()

    assert response['location'] == thread.get_absolute_url()
    assert message.sender == logged_in.user
    assert message.message == payload['message']


@pytest.mark.django_db
def test_send_message_view_existing_thread(logged_in):
    user = users.factories.UserFactory()
    ad = ads.factories.AdFactory(user=user)
    thread = messaging.factories.ThreadFactory(users=[user, logged_in.user], ad=ad)

    payload = {'ad_id': ad.pk, 'message': 'Hello!'}
    response = logged_in.client.post(reverse('messaging:send_message'), payload)

    assert response.status_code == 302
    assert response['location'] == thread.get_absolute_url()

    message = apps.get_model('messaging', 'Message').objects.filter(thread=thread.pk).last()

    assert message.sender == logged_in.user
    assert message.message == payload['message']


@pytest.mark.django_db
def test_send_message_view_empty_message(logged_in):
    user = users.factories.UserFactory()
    ad = ads.factories.AdFactory(user=user)

    payload = {'ad_id': ad.pk, 'message': ''}
    response = logged_in.client.post(reverse('messaging:send_message'), payload)

    assert response.status_code == 400


@pytest.mark.django_db
def test_send_message_view_blocked_thread(logged_in):
    user = users.factories.UserFactory()
    ad = ads.factories.AdFactory(user=user)
    messaging.factories.ThreadFactory(users=[user, logged_in.user], ad=ad, blocked=True)

    payload = {'ad_id': ad.pk, 'message': 'Hello!'}
    response = logged_in.client.post(reverse('messaging:send_message'), payload)

    assert response.status_code == 400


@pytest.mark.django_db
def test_send_message_view_invalid_ad(logged_in):
    payload = {'ad_id': 0, 'message': 'Hello!'}
    response = logged_in.client.post(reverse('messaging:send_message'), payload)

    assert response.status_code == 404
