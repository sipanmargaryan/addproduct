import pytest

from django.contrib.auth import get_user_model

from users.factories import UserFactory


@pytest.mark.django_db
def test_auth_user_model_setup():
    UserFactory.create_batch(10)

    assert get_user_model().objects.count() == 10


@pytest.mark.django_db
def test_create_user():
    get_user_model().objects.create_user('email@example.com', 'password')

    assert get_user_model().objects.filter(
        email='email@example.com', is_staff=False, is_superuser=False,
    ).count()


@pytest.mark.django_db
def test_create_super_user():
    get_user_model().objects.create_superuser('email@example.com', 'password')

    assert get_user_model().objects.filter(
        email='email@example.com', is_staff=True, is_superuser=True,
    ).count()
