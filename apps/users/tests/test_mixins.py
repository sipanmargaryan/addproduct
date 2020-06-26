import pytest

from django.apps import apps

import core.testing
import users.mixins


@pytest.mark.django_db
def test_social_mixin(monkeypatch):
    monkeypatch.setattr('requests.get', lambda url: core.testing.response(200, b'image'))

    authentication_data = {
        'email': 'email@example.com',
        'first_name': 'John',
        'last_name': 'Doe',
        'avatar_url': 'http://example.com/avatar.png',
        'provider': 'facebook',
        'provider_id': 'provider_id',
    }
    user = users.mixins.SocialAuthMixin.set_social_user(authentication_data)

    assert user

    assert apps.get_model('users', 'SocialConnection').objects.filter(
        provider=authentication_data['provider'],
        provider_id=authentication_data['provider_id'],
        user=user,
    ).first()


@pytest.mark.django_db
def test_social_mixin_invalid():
    assert not users.mixins.SocialAuthMixin.set_social_user({'email': None})
