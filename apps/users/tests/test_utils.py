import pytest

import core.testing
import users.utils


@pytest.mark.parametrize('provider', ['facebook', 'google', 'instagram', 'twitter'])
def test_social_request_token_uri(provider, settings):
    builder = users.utils.SocialTokenRequestURIBuilder()
    uri = builder.build_token_request_uri(provider)

    assert provider in uri
    if provider != 'twitter':
        assert getattr(settings, f'SOCIAL_{provider.upper()}_KEY') in uri


def test_social_request_token_uri_invalid():
    builder = users.utils.SocialTokenRequestURIBuilder()
    uri = builder.build_token_request_uri('invalid')

    assert not uri


@pytest.mark.parametrize('provider', ['facebook', 'google', 'instagram', 'twitter'])
def test_social_user_retriever(provider, monkeypatch):
    monkeypatch.setattr(
        f'users.utils.SocialUserRetriever.retrieve_{provider.lower()}_user',
        lambda self, code: True,
    )
    assert users.utils.SocialUserRetriever().retrieve_user(provider=provider, code='code')


def test_retrieve_facebook_user(monkeypatch):
    auth_code = '0' * 10
    auth_token = '1' * 10
    social_user = {'id': '1', 'email': 'email@example.com', 'first_name': 'John', 'last_name': 'Doe'}

    def social_mock(url):
        if '&code=' in url:
            assert auth_code in url
            content = {'access_token': auth_token}
        else:
            assert auth_token in url
            content = social_user

        return core.testing.response(200, content)

    monkeypatch.setattr('requests.get', social_mock)
    user = users.utils.SocialUserRetriever().retrieve_facebook_user(auth_code)

    del user['avatar_url']

    assert sorted(user.values()) == sorted(social_user.values())


def test_retrieve_instagram_user(monkeypatch):
    auth_code = '0' * 10
    social_user = {
        'user': {'id': '1', 'full_name': 'John Doe', 'profile_picture': 'http://example.com/avatar.png'}
    }

    def social_mock(url, params):
        assert auth_code == params['code']
        return core.testing.response(200, social_user)

    monkeypatch.setattr('requests.post', social_mock)
    user = users.utils.SocialUserRetriever().retrieve_instagram_user(auth_code)

    assert user['first_name'] == 'John'
    assert user['last_name'] == 'Doe'
    assert user['avatar_url'] == social_user['user']['profile_picture']


def test_retrieve_google_user(monkeypatch):
    auth_code = '0' * 10
    auth_token = '1' * 10
    social_user = {
        'id': '1', 'email': 'email@example.com', 'picture': 'http://example.com/avatar.png',
        'given_name': 'John', 'family_name': 'Doe',
    }

    def social_mock(url, params=None):
        if params:
            assert auth_code == params['code']
            content = {'access_token': auth_token}
        else:
            assert auth_token in url
            content = social_user

        return core.testing.response(200, content)

    monkeypatch.setattr('requests.get', social_mock)
    monkeypatch.setattr('requests.post', social_mock)
    user = users.utils.SocialUserRetriever().retrieve_google_user(auth_code)

    assert sorted(social_user.values()) == sorted(user.values())
