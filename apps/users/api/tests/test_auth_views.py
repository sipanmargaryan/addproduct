import pytest

from django.urls import reverse
from django.utils import timezone

from core.utils import build_client_absolute_url
from users.factories import UserFactory
from users.models import User


@pytest.mark.django_db
def test_auth(client):
    user = UserFactory()
    user.set_password('password')
    user.save()

    payload = dict(
        email=user.email,
        password='password',
    )

    response = client.post(reverse('users_api:login'), payload)
    assert response.status_code == 200

    response = response.json()
    assert 'access_token' in response
    assert 'refresh_token' in response


@pytest.mark.django_db
def test_auth_invalid(client):
    payload = dict(
        email='invalid email',
        password='invalid password',
    )

    response = client.post(reverse('users_api:login'), payload)
    assert response.status_code == 400

    user = UserFactory()
    payload = dict(
        email=user.email,
        password='invalid password',
    )

    response = client.post(reverse('users_api:login'), payload)
    assert response.status_code == 400


@pytest.mark.django_db
def test_signup(client, mailoutbox, settings):
    payload = dict(
        full_name='john doe',
        email='mail@example.com',
        password='n0nNumer1C',
        phone_number='+ 123 456-789',
    )

    response = client.post(reverse('users_api:signup'), payload)
    assert response.status_code == 201

    assert len(mailoutbox) == 1

    msg = mailoutbox[0]

    assert msg.subject == 'Confirm your registration at {site_name}'.format(
        site_name=settings.SITE_NAME
    )
    assert msg.to == [payload['email']]

    user = User.objects.filter(email=payload['email']).first()
    email_confirmation_path = '/accounts/confirm-email/{token}'.format(
        token=user.email_confirmation_token
    )
    assert build_client_absolute_url(email_confirmation_path) in msg.body


@pytest.mark.django_db
def test_signup_invalid(client):
    response = client.post(reverse('users_api:signup'), dict())
    assert response.status_code == 400
    response = response.json()

    assert response['email'] == ['This field is required.']
    assert response['password'] == ['This field is required.']
    assert response['full_name'] == ['This field is required.']

    payload = dict(
        email='invalid',
        password='password',
        full_name='invalid',
        phone_number='invalid',
    )
    response = client.post(reverse('users_api:signup'), payload)
    assert response.status_code == 400
    response = response.json()

    assert response['full_name'] == ['Provided name is invalid.']
    assert response['password'] == ['This password is too common.']
    assert response['email'] == ['Enter a valid email address.']

    user = UserFactory()
    payload['full_name'] = ' invalid  '
    payload['email'] = user.email
    response = client.post(reverse('users_api:signup'), payload)

    assert response.status_code == 400

    response = response.json()

    assert response['full_name'] == ['Provided name is invalid.']
    assert response['email'] == ['user with this email already exists.']


@pytest.mark.django_db
def test_email_confirmation(client):
    user = UserFactory(is_active=False, email_confirmation_token=User.generate_token())

    payload = dict(token=user.email_confirmation_token)

    response = client.post(reverse('users_api:confirm_email_address'), payload)
    user.refresh_from_db()

    assert response.status_code == 200
    response = response.json()
    assert response['user']['pk'] == user.pk
    assert 'access_token' in response
    assert 'refresh_token' in response
    assert user.email_confirmation_token is None
    assert user.is_active is True


@pytest.mark.django_db
def test_email_confirmation_invalid(client):
    UserFactory(is_active=False, email_confirmation_token=User.generate_token())

    payload = dict(token='invalid token')

    response = client.post(reverse('users_api:confirm_email_address'), payload)
    assert response.status_code == 400


@pytest.mark.django_db
def test_forgot_password(client, mailoutbox, settings):
    user = UserFactory()

    payload = dict(email=user.email)

    response = client.post(reverse('users_api:forgot_password'), payload)
    assert response.status_code == 200

    assert len(mailoutbox) == 1

    msg = mailoutbox[0]

    assert msg.subject == 'Reset your {site_name} password'.format(
        site_name=settings.SITE_NAME
    )
    assert msg.to == [payload['email']]

    user = User.objects.filter(email=user.email).first()
    reset_password_path = '/accounts/reset-password/{token}'.format(
        token=user.reset_password_token
    )

    assert build_client_absolute_url(reset_password_path) in msg.body


@pytest.mark.django_db
def test_forgot_password_invalid(client):
    payload = dict(email='email@example.com')

    response = client.post(reverse('users_api:forgot_password'), payload)
    assert response.status_code == 200

    user = UserFactory(is_active=False)
    payload = dict(email=user.email)

    response = client.post(reverse('users_api:forgot_password'), payload)
    assert response.status_code == 200


@pytest.mark.django_db
def test_reset_password(client):
    user = UserFactory(
        is_active=False,
        reset_password_token=User.generate_token(),
        reset_password_request_date=timezone.now(),
    )

    new_password = user.reset_password_token
    payload = dict(
        token=user.reset_password_token,
        password=new_password,
    )

    response = client.post(reverse('users_api:reset_password'), payload)
    assert response.status_code == 200

    user.refresh_from_db()
    response = response.json()

    assert user.pk == response['user']['pk']
    assert user.is_active is True
    assert user.check_password(new_password) is True
    assert 'access_token' in response
    assert 'refresh_token' in response


@pytest.mark.django_db
def test_reset_password_expired(client):
    user = UserFactory(
        reset_password_token=User.generate_token(),
        reset_password_request_date=timezone.now() - timezone.timedelta(minutes=5),
    )

    payload = dict(
        token=user.reset_password_token,
        password='password',
    )

    response = client.post(reverse('users_api:reset_password'), payload)
    assert response.status_code == 400


@pytest.mark.django_db
def test_reset_password_invalid_token(client):
    UserFactory(
        reset_password_token=User.generate_token(),
        reset_password_request_date=timezone.now(),
    )

    payload = dict(
        token='token',
        password='password',
    )

    response = client.post(reverse('users_api:reset_password'), payload)
    assert response.status_code == 400
