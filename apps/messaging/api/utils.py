import json

import requests
from channels.auth import AuthMiddlewareStack
from rest_framework_simplejwt.settings import api_settings

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.db import close_old_connections

__all__ = (
    'Firebase',
    'TokenAuthMiddlewareStack',
)


class Firebase(object):

    def __init__(self):
        self.headers = {
            'Content-Type': 'application/json',
            'Authorization': f'key={settings.FCM_SERVER_KEY}',
        }
        self.url = 'https://fcm.googleapis.com/fcm/send'

    async def send_message(self, message_data, registration_ids, badge=1):
        message = {
            'body': message_data['message'],
            'title': 'New Message',
            'sound': 'default',
            'badge': badge,
            'icon': 'ic_notification',
        }

        payload = {
            'priority': 'high',
            'notification': message,
            'data': message_data,
            'registration_ids': registration_ids,
        }

        return requests.post(self.url, json.dumps(payload), headers=self.headers)

    async def send_down_stream_message(self, message_data, registration_ids):

        payload = {
            'data': message_data,
            'registration_ids': registration_ids,
        }

        return requests.post(self.url, json.dumps(payload), headers=self.headers)


class TokenAuthMiddleware:

    def __init__(self, inner):
        self.inner = inner

    def __call__(self, scope):
        if 'query_string' in scope:
            try:
                token_name, raw_token = scope['query_string'].decode().split('=')
                if token_name == 'token':
                    validated_token = self.get_validated_token(raw_token)
                    if validated_token:
                        scope['user'] = self.get_user(validated_token)
                        close_old_connections()
                    else:
                        scope['user'] = AnonymousUser()
            except:  # noqa
                pass

        return self.inner(scope)

    @staticmethod
    def get_validated_token(raw_token):
        """
        Validates an encoded JSON web token and returns a validated token
        wrapper object.
        """
        for AuthToken in api_settings.AUTH_TOKEN_CLASSES:
            try:
                return AuthToken(raw_token)
            except:  # noqa
                pass

    @staticmethod
    def get_user(validated_token):
        """
        Attempts to find and return a user using the given validated token.
        """
        try:
            user_id = validated_token[api_settings.USER_ID_CLAIM]
        except KeyError:
            return None

        return (
            get_user_model().objects
            .filter(**{api_settings.USER_ID_FIELD: user_id, 'is_active': True})
            .first()
        )


def middleware(inner):
    return TokenAuthMiddleware(AuthMiddlewareStack(inner))


TokenAuthMiddlewareStack = middleware
