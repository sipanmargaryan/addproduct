import base64

from django import http
from django.conf import settings


class BasicAuthMiddleware(object):

    disabled_for_methods = {
        'OPTIONS',
    }

    def __init__(self, get_response=None):
        self.get_response = get_response
        super(BasicAuthMiddleware, self).__init__()

    def __call__(self, request):
        response = None
        if hasattr(self, 'process_request'):
            response = self.process_request(request)
        if not response:
            response = self.get_response(request)
        if hasattr(self, 'process_response'):
            response = self.process_response(request, response)
        return response

    # noinspection PyMethodMayBeStatic
    def process_request(self, request):

        if request.method in self.disabled_for_methods:
            return

        basic_auth = settings.ENABLE_HTTP_BASIC_AUTH
        basic_auth_settings = settings.HTTP_BASIC_AUTH
        if not basic_auth or not basic_auth_settings:
            return

        exclude_urls = settings.HTTP_BASIC_AUTH_EXCLUDE_URLS
        for url in exclude_urls:
            if request.path.startswith(url):
                return

        for username, password in basic_auth_settings.items():
            authorization_string = 'Basic {}'.format(
                base64.b64encode(
                    '{username}:{password}'.format(username=username, password=password).encode()
                ).decode()
            )
            if request.META.get('HTTP_AUTHORIZATION') == authorization_string:
                return

        response = http.HttpResponse(status=401)
        response['WWW-Authenticate'] = 'Basic realm="{}"'.format(settings.CLIENT_DOMAIN)
        return response
