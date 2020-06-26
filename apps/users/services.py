import birdy.twitter
import pydash
import requests

from django.conf import settings

FACEBOOK_API_URL = 'https://graph.facebook.com/v3.2/'
GOOGLE_API_URL = 'https://www.googleapis.com/'
INSTAGRAM_API_URL = 'https://api.instagram.com/v1/'


__all__ = (
    'facebook_retrieve_user',
    'google_retrieve_user',
    'instagram_retrieve_user',
    'twitter_retrieve_user',
)


def facebook_retrieve_user(access_token: str) -> dict:
    """
    Retrieve facebook user information
    :param access_token:
    :return: dict
    """
    fields = 'id', 'first_name', 'last_name', 'email', 'picture{url}'
    endpoint = 'me?fields={}'.format(','.join(fields))
    endpoint += f'&access_token={access_token}'

    response = requests.get(FACEBOOK_API_URL + endpoint)

    if response.status_code == 200:
        user = response.json()
        result = dict(
            provider_id=user['id'],
            email=user.get('email', f'{user["id"]}@facebook.com'),
            avatar_url=f'https://graph.facebook.com/{user["id"]}/picture?width=250',
            first_name=user['first_name'],
            last_name=user['last_name'],
        )
    else:
        result = dict(error=pydash.get(response.json(), 'error.message'))

    return result


def google_retrieve_user(access_token: str) -> dict:
    """
    Retrieve google user information
    :param access_token:
    :return: dict
    """
    endpoint = 'oauth2/v2/userinfo'

    response = requests.get(
        GOOGLE_API_URL + endpoint,
        headers={'Authorization': f'Bearer {access_token}'},
    )

    if response.status_code == 200:
        user = response.json()
        result = dict(
            provider_id=user['id'],
            email=user['email'],
            avatar_url=user['picture'],
            first_name=user['given_name'],
            last_name=user['family_name'],
        )
    else:
        result = dict(error=response.json().get('error_description', None))

    return result


def instagram_retrieve_user(access_token: str) -> dict:
    """
    Retrieve instagram user information
    :param access_token:
    :return: dict
    """
    endpoint = f'users/self/?access_token={access_token}'

    response = requests.get(INSTAGRAM_API_URL + endpoint)

    if response.status_code == 200:
        user = response.json()['data']

        try:
            f_name, l_name = user['full_name'].split(' ', 1)
        except ValueError:
            f_name = user['full_name']
            l_name = user['full_name']

        result = dict(
            provider_id=user['id'],
            avatar_url=user['profile_picture'],
            first_name=f_name,
            last_name=l_name,
        )
    else:
        result = dict(error=pydash.get(response.json(), 'meta.error_message', None))

    return result


def twitter_retrieve_user(oauth_token: str, oauth_token_secret: str) -> dict:
    """
    Retrieve twitter user information
    :type oauth_token: str
    :type oauth_token_secret: str
    :return: dict
    """
    client = birdy.twitter.UserClient(
        settings.SOCIAL_TWITTER_CONSUMER_KEY,
        settings.SOCIAL_TWITTER_CONSUMER_SECRET,
        oauth_token, oauth_token_secret,
    )

    response = client.api['account']['verify_credentials'].get()

    try:
        first_name, last_name = response.data.get('name').split(' ', 1)
    except (ValueError, AttributeError):
        first_name = last_name = None

    return dict(
        provider_id=response.data.get('id'),
        avatar_url=response.data.get('profile_image_url_https'),
        first_name=first_name,
        last_name=last_name,
    )
