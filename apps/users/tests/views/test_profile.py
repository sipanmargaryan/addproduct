import json

import pytest

from django.urls import reverse

from core.factories import CityFactory


@pytest.mark.django_db
def test_profile_retrieve(client, auth_user):
    client.login(email=auth_user.email, password='password')
    response = client.get(reverse('users:profile'))
    assert response.status_code == 200


@pytest.mark.django_db
def test_contact_info(logged_in, image_file):
    user = logged_in.user
    city = CityFactory()

    payload = {
        'full_name': 'John Doe',
        'email': 'email@example.com',
        'phone_number': '+123 456-789',
        'city': city.id,
        'avatar': image_file(),
    }
    response = logged_in.client.post(reverse('users:contact_info'), payload)
    user.refresh_from_db()

    assert response.status_code == 204
    assert {user.first_name, user.last_name} == {*payload['full_name'].split(' ', 1)}
    assert user.email == payload['email']
    assert user.city.id == payload['city']
    assert user.phone_number == payload['phone_number']
    assert user.avatar.url[-4:] == '.png'


@pytest.mark.django_db
def test_contact_info_invalid(logged_in):
    city = CityFactory()

    payload = {
        'email': 'email@example.com',
        'full_name': 'John',
        'phone_number': '+123 456-789',
        'city': city.id,
    }

    response = logged_in.client.post(reverse('users:contact_info'), payload)

    assert response.status_code == 400
    response = json.loads(response.content)
    assert response['full_name'][0] == 'Make sure you have first and last names included.'

    payload['email'] = ''

    response = logged_in.client.post(reverse('users:contact_info'), payload)

    assert response.status_code == 400
    response = json.loads(response.content)
    assert response.get('email', False)


@pytest.mark.django_db
def test_change_password(logged_in):
    user = logged_in.user
    payload = {
        'old_password': 'password',
        'password': 'new_password',
        'password_confirmation': 'new_password',
    }

    response = logged_in.client.post(reverse('users:change_password'), payload)
    user.refresh_from_db()

    assert response.status_code == 204
    assert user.check_password(payload['password'])


@pytest.mark.django_db
def test_change_password_invalid(logged_in):
    payload = {
        'old_password': 'wrong',
        'password': 'new_password',
        'password_confirmation': 'new_password',
    }

    response = logged_in.client.post(reverse('users:change_password'), payload)
    assert response.status_code == 400
    response = json.loads(response.content)
    assert response['old_password'][0] == 'Current password is incorrect.'

    payload['password_confirmation'] = 'not_match'

    response = logged_in.client.post(reverse('users:change_password'), payload)
    assert response.status_code == 400
    response = json.loads(response.content)
    assert response['password_confirmation'][0] == 'Passwords didn\'t match.'


@pytest.mark.django_db
def test_notification_settings(logged_in):
    user = logged_in.user
    payload = {
        'ad_answer': 'yes',
        'news_offer_promotion': 'no',
    }

    response = logged_in.client.post(reverse('users:notification_settings'), payload)
    user.refresh_from_db()

    assert response.status_code == 204
    assert user.notification.ad_answer
    assert not user.notification.news_offer_promotion


@pytest.mark.django_db
def test_notification_settings_invalid(logged_in):
    user = logged_in.user

    payload = {
        'news_offer_promotion': 'no',
    }

    response = logged_in.client.post(reverse('users:notification_settings'), payload)
    user.refresh_from_db()

    assert response.status_code == 400
    assert user.notification.ad_answer
    assert user.notification.news_offer_promotion
