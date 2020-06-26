from typing import Optional

import birdy.twitter
import requests

from django.conf import settings
from django.core.cache import cache
from django.urls import reverse

from core.utils import build_client_absolute_url
from users.models import SocialConnection


class SocialParams(object):
    CALLBACK_URL = 'users:oauth_complete'


class SocialTokenRequestURIBuilder(SocialParams):

    def build_token_request_uri(self, provider: str) -> Optional[str]:
        if provider not in SocialConnection.providers():
            return

        builder = getattr(self, f'build_{provider}_url')
        return builder()

    def build_facebook_url(self):
        token_request_uri = 'https://graph.facebook.com/oauth/authorize'
        params = {
            'client_id': settings.SOCIAL_FACEBOOK_KEY,
            'scope': 'email',
        }

        return self.construct_uri(token_request_uri, params, provider='facebook')

    def build_instagram_url(self):
        token_request_uri = 'https://api.instagram.com/oauth/authorize/'
        params = {
            'client_id': settings.SOCIAL_INSTAGRAM_KEY,
            'response_type': 'code',
        }

        return self.construct_uri(token_request_uri, params, provider='instagram')

    def build_google_url(self):
        token_request_uri = 'https://accounts.google.com/o/oauth2/auth'
        params = {
            'client_id': settings.SOCIAL_GOOGLE_KEY,
            'response_type': 'code',
            'scope': ' '.join([
                'https://www.googleapis.com/auth/userinfo.profile',
                'https://www.googleapis.com/auth/userinfo.email',
            ]),
        }

        return self.construct_uri(token_request_uri, params, provider='google')

    def build_twitter_url(self):
        redirect_uri = reverse(self.CALLBACK_URL, kwargs={'provider': 'twitter'})
        client = birdy.twitter.UserClient(
            settings.SOCIAL_TWITTER_CONSUMER_KEY, settings.SOCIAL_TWITTER_CONSUMER_SECRET
        )

        token = client.get_signin_token(build_client_absolute_url(redirect_uri))

        cache.set(token.oauth_token, token.oauth_token_secret, 30)

        return token.auth_url

    def construct_uri(self, token_request_uri: str, params: dict, provider: str) -> str:
        redirect_uri = reverse(self.CALLBACK_URL, kwargs={'provider': provider})

        params['redirect_uri'] = build_client_absolute_url(redirect_uri)

        token_request_uri += '?'
        token_request_uri += '&'.join(['{}={}'.format(*item) for item in params.items()])
        print(token_request_uri)
        return token_request_uri


class SocialUserRetriever(SocialParams):

    def retrieve_user(self, *, provider, **kwargs) -> Optional[dict]:
        if provider not in SocialConnection.providers():
            return

        retriever = getattr(self, f'retrieve_{provider}_user')
        filtered = {key: value for key, value in kwargs.items() if value is not None}

        if not filtered:
            return

        return retriever(**filtered)

    def retrieve_facebook_user(self, code: str) -> Optional[dict]:
        access_token_uri = 'https://graph.facebook.com/v3.2/oauth/access_token'
        redirect_uri = reverse(self.CALLBACK_URL, kwargs={'provider': 'facebook'})
        params = {
            'client_id': settings.SOCIAL_FACEBOOK_KEY,
            'client_secret': settings.SOCIAL_FACEBOOK_SECRET,
            'redirect_uri': build_client_absolute_url(redirect_uri),
            'code': code,
        }

        access_token_uri += '?'
        access_token_uri += '&'.join(['{}={}'.format(*item) for item in params.items()])

        response = requests.get(access_token_uri)

        if response.status_code != 200:
            return

        access_token = response.json()['access_token']

        fields = 'id', 'first_name', 'last_name', 'email', 'picture{url}'
        user_info_uri = 'https://graph.facebook.com/v3.2/'
        user_info_uri += 'me?fields={}'.format(','.join(fields))
        user_info_uri += f'&access_token={access_token}'

        response = requests.get(user_info_uri)

        if response.status_code != 200:
            return

        user = response.json()

        return dict(
            provider_id=user['id'],
            email=user.get('email', None),
            avatar_url=f'https://graph.facebook.com/{user["id"]}/picture?width=250',
            first_name=user['first_name'],
            last_name=user['last_name'],
        )

    def retrieve_instagram_user(self, code: str) -> Optional[dict]:
        access_token_uri = 'https://api.instagram.com/oauth/access_token'
        redirect_uri = reverse(self.CALLBACK_URL, kwargs={'provider': 'instagram'})
        payload = {
            'client_id': settings.SOCIAL_INSTAGRAM_KEY,
            'client_secret': settings.SOCIAL_INSTAGRAM_SECRET,
            'redirect_uri': build_client_absolute_url(redirect_uri),
            'grant_type': 'authorization_code',
            'code': code,
        }

        response = requests.post(access_token_uri, payload)

        if response.status_code != 200:
            return

        user = response.json()['user']
        first_name, last_name = user['full_name'].split(' ', 1)

        return dict(
            provider_id=user['id'],
            email=None,
            avatar_url=user['profile_picture'],
            first_name=first_name,
            last_name=last_name,
        )

    def retrieve_google_user(self, code: str) -> Optional[dict]:
        access_token_uri = 'https://accounts.google.com/o/oauth2/token'
        user_info_uri = 'https://www.googleapis.com/oauth2/v1/userinfo'
        redirect_uri = reverse(self.CALLBACK_URL, kwargs={'provider': 'google'})
        payload = {
            'code': code,
            'redirect_uri': build_client_absolute_url(redirect_uri),
            'client_id': settings.SOCIAL_GOOGLE_KEY,
            'client_secret': settings.SOCIAL_GOOGLE_SECRET,
            'grant_type': 'authorization_code',
        }

        response = requests.post(access_token_uri, payload)

        if not response.status_code == 200:
            return

        access_token = response.json()['access_token']

        response = requests.get(f'{user_info_uri}?access_token={access_token}')

        if not response.status_code == 200:
            return

        user = response.json()

        return dict(
            provider_id=user['id'],
            email=user['email'],
            avatar_url=user['picture'],
            first_name=user['given_name'],
            last_name=user['family_name'],
        )

    # noinspection PyMethodMayBeStatic
    def retrieve_twitter_user(self, oauth_token: str, oauth_verifier: str) -> Optional[dict]:
        if not oauth_token or not oauth_verifier:
            return

        oauth_token_secret = cache.get(oauth_token)
        cache.delete('oauth_token')
        if not oauth_token_secret:
            return

        client = birdy.twitter.UserClient(
            settings.SOCIAL_TWITTER_CONSUMER_KEY,
            settings.SOCIAL_TWITTER_CONSUMER_SECRET,
            oauth_token, oauth_token_secret,
        )

        token = client.get_access_token(oauth_verifier)

        screen_name = token.get('screen_name')
        if not screen_name:
            return None

        response = client.api['users']['show'].get(screen_name=screen_name)

        try:
            first_name, last_name = response.data.get('name').split(' ', 1)
        except (ValueError, AttributeError):
            first_name = last_name = None

        return dict(
            provider_id=response.data.get('id'),
            email=None,
            avatar_url=response.data.get('profile_image_url_https'),
            first_name=first_name,
            last_name=last_name,
        )
