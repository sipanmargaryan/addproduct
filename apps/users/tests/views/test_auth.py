import copy

import pytest

from django.apps import apps
from django.contrib.auth import get_user_model
from django.urls import reverse

import core.testing
from users.factories import UserFactory


@pytest.mark.django_db
def test_login(client):
    user = UserFactory()
    user.set_password('password')
    user.save()

    payload = {
        'email': user.email,
        'password': 'password',
    }

    response = client.post(f'{reverse("users:login")}?next={reverse("users:profile")}', payload)
    assert response.status_code == 302
    assert response['location'] == reverse('users:profile')


@pytest.mark.django_db
def test_login_invalid(client):

    payload = {
        'email': 'invalid@example.com',
        'password': 'password',
    }

    response = client.post(reverse('users:login'), payload)
    assert response.status_code == 200


@pytest.mark.django_db
def test_signup(client, mailoutbox):
    payload = {
        'email': 'email@example.com',
        'password': 'n0nNumer1C',
        'full_name': 'John Doe',
        'phone_number': '+ 123 456-789',
    }

    response = client.post(reverse('users:signup'), payload)
    user = get_user_model().objects.first()

    assert response.status_code == 302
    assert response['location'] == reverse('users:signup_success', kwargs={'email': payload['email']})
    assert not user.is_active
    assert user.first_name == 'John'
    assert user.last_name == 'Doe'
    assert user.phone_number == payload['phone_number']
    assert user.email == payload['email']
    assert user.check_password(payload['password'])
    assert hasattr(user, 'notification')

    assert len(mailoutbox) == 1
    message = mailoutbox[0]
    assert message.to == [payload['email']]
    assert message.body.find(user.email_confirmation_token)


@pytest.mark.django_db
def test_signup_invalid(client, mailoutbox):
    payload = {
        'email': 'email@example.com',
        'password': 'n0nNumer1C',
        'full_name': 'John',
        'phone_number': '+123 456-789',
    }

    response = client.post(reverse('users:signup'), payload)
    assert response.status_code == 200
    assert get_user_model().objects.count() == 0

    user = UserFactory()
    payload['full_name'] = 'John Doe'
    payload['email'] = user.email

    response = client.post(reverse('users:signup'), payload)
    assert response.status_code == 200
    assert get_user_model().objects.count() == 1

    assert not len(mailoutbox)


def test_signup_success(client):
    email = 'email@example.com'

    response = client.get(reverse('users:signup_success', kwargs={'email': email}))
    assert response.status_code == 200
    assert response.context['email_address'] == email


@pytest.mark.django_db
def test_confirm_email(client):
    user = UserFactory(is_active=False)
    user.email_confirmation_token = user.generate_token()
    user.save()

    confirm_url = reverse('users:confirm_email', kwargs={'token': user.email_confirmation_token})
    response = client.get(f'{confirm_url}?next={reverse("users:profile")}')
    user.refresh_from_db()

    assert response.status_code == 302
    assert response['location'] == reverse('users:profile')
    assert user.is_active
    assert not user.email_confirmation_token


@pytest.mark.django_db
def test_confirm_email_invalid(client):
    user = UserFactory(is_active=False)
    user.email_confirmation_token = user.generate_token()
    user.save()

    response = client.get(reverse('users:confirm_email', kwargs={'token': 'invalid_token'}))
    user.refresh_from_db()

    assert response.status_code == 404
    assert not user.is_active
    assert user.email_confirmation_token


@pytest.mark.django_db
def test_forgot_password(client, mailoutbox):
    user = UserFactory()
    assert not user.reset_password_token

    response = client.post(reverse('users:forgot_password'), {'email': user.email})
    user.refresh_from_db()

    assert response.status_code == 302
    assert response['location'] == reverse('users:forgot_password_success')
    assert user.reset_password_token

    assert len(mailoutbox) == 1
    message = mailoutbox[0]
    assert message.to == [user.email]
    assert message.body.find(user.reset_password_token)


@pytest.mark.django_db
def test_forgot_password_invalid(client):
    response = client.post(reverse('users:forgot_password'), {'email': 'email@example.com'})

    assert response.status_code == 302
    assert response['location'] == reverse('users:forgot_password_success')


@pytest.mark.django_db
def test_reset_password(client):
    user = UserFactory()
    user.reset_password_token = user.generate_token()
    user.save()

    payload = {
        'password': 'n0nNumer1C',
        'password_confirmation': 'n0nNumer1C',
    }

    reset_url = reverse('users:reset_password', kwargs={'token': user.reset_password_token})
    response = client.post(f'{reset_url}?next={reverse("users:profile")}', payload)
    user.refresh_from_db()

    assert response.status_code == 302
    assert response['location'] == reverse('users:profile')
    assert user.check_password(payload['password'])
    assert not user.reset_password_token


@pytest.mark.django_db
def test_reset_password_invalid(client):
    user = UserFactory()
    user.reset_password_token = user.generate_token()
    user.save()

    payload = {
        'password': 'newpass',
        'password_confirmation': 'wrongpass',
    }

    response = client.post(reverse('users:reset_password', kwargs={'token': user.reset_password_token}), payload)
    user.refresh_from_db()

    assert response.status_code == 200
    assert not user.check_password(payload['password'])
    assert user.reset_password_token

    payload['password_confirmation'] = payload['password']
    response = client.post(reverse('users:reset_password', kwargs={'token': 'invalid_token'}), payload)
    user.refresh_from_db()

    assert response.status_code == 404
    assert not user.check_password(payload['password'])
    assert user.reset_password_token


@pytest.mark.django_db
def test_logout(logged_in, settings):
    response = logged_in.client.get(reverse('users:logout'))
    assert response.status_code == 302
    assert response['location'] == settings.LOGOUT_REDIRECT_URL


@pytest.mark.django_db
def test_oauth_complete(client, monkeypatch):
    auth_code = '0' * 10
    provider = 'facebook'
    social_user = {
        'provider_id': '1', 'email': 'email@example.com',
        'first_name': 'John', 'last_name': 'Doe', 'avatar_url': 'http://example.com/avatar.png',
    }

    def retrieve_user(*args, **kwargs):
        assert kwargs['code'] == auth_code
        return copy.copy(social_user)

    monkeypatch.setattr('users.utils.SocialUserRetriever.retrieve_user', retrieve_user)
    monkeypatch.setattr('requests.get', lambda url: core.testing.response(200, b'image'))

    response = client.get('{}?code={}'.format(
        reverse('users:oauth_complete', kwargs={'provider': provider}), auth_code
    ))

    assert response.status_code == 302
    assert response['location'] == '/'

    user = get_user_model().objects.filter(email=social_user['email']).first()

    assert user
    assert apps.get_model('users', 'SocialConnection').objects.filter(
        provider=provider,
        provider_id=social_user['provider_id'],
        user=user,
    ).first()


@pytest.mark.django_db
def test_oauth_complete_oauth_email(client, monkeypatch):
    auth_code = '0' * 10
    social_user = {'provider_id': '1', 'email': 'email@example.com'}

    def nothing(*args, **kwargs):
        return

    def retrieve_user(*args, **kwargs):
        return copy.copy(social_user)

    monkeypatch.setattr('users.utils.SocialUserRetriever.retrieve_user', retrieve_user)
    monkeypatch.setattr('users.views.OAuthCompleteView.get_social_user', nothing)
    monkeypatch.setattr('users.views.OAuthCompleteView.set_social_user', nothing)

    response = client.get('{}?code={}'.format(
        reverse('users:oauth_complete', kwargs={'provider': 'provider'}), auth_code
    ))

    assert response.status_code == 302
    assert response['location'] == reverse('users:oauth_email')


@pytest.mark.parametrize('provider', ['facebook', 'google', 'instagram', 'twitter'])
def test_oauth_redirect(provider, client):
    response = client.get(reverse('users:oauth', kwargs={'provider': provider}))
    assert response.status_code == 302


def test_oauth_redirect_invalid(client):
    response = client.get(reverse('users:oauth', kwargs={'provider': 'invalid'}))
    assert response.status_code == 404


@pytest.mark.django_db
def test_oauth_email(client, client_session, monkeypatch):
    monkeypatch.setattr('requests.get', lambda url: core.testing.response(200, b'image'))

    payload = {'email': 'email@example.com'}
    authentication_data = {
        'first_name': 'John',
        'last_name': 'Doe',
        'avatar_url': 'http://example.com/avatar.png',
        'provider': 'facebook',
        'provider_id': 'provider_id',
    }
    client_session['authentication_data'] = authentication_data
    client_session.save()
    response = client.post(reverse('users:oauth_email'), payload)

    assert response.status_code == 302

    user = apps.get_model('users', 'User').objects.filter(**payload).first()

    assert user

    assert apps.get_model('users', 'SocialConnection').objects.filter(
        provider=authentication_data['provider'],
        provider_id=authentication_data['provider_id'],
        user=user,
    ).first()


@pytest.mark.django_db
def test_oauth_email_invalid(client):
    payload = {'email': 'email@example.com'}
    response = client.post(reverse('users:oauth_email'), payload)

    assert response.status_code == 302
    assert apps.get_model('users', 'SocialConnection').objects.count() == 0

    UserFactory(**payload)
    response = client.post(reverse('users:oauth_email'), payload)

    assert response.status_code == 200
    assert apps.get_model('users', 'SocialConnection').objects.count() == 0
