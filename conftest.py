from importlib import import_module
import types
import os
import shutil

import pytest

from channels.testing import WebsocketCommunicator

from django.core.files.uploadedfile import SimpleUploadedFile


from project.routing import application
from core.testing import create_image
from users.factories import UserFactory


@pytest.fixture
def auth_user() -> UserFactory:
    """
    User with simple password.
    :return: UserFactory
    """
    user = UserFactory()
    user.set_password('password')
    user.save()

    return user


@pytest.fixture
def logged_in(client, auth_user) -> types.SimpleNamespace:
    """
    Client with already logged in user to make authenticated requests.
    :param client:
    :param auth_user:
    :return: dict
    """
    client.login(email=auth_user.email, password='password')

    result = types.SimpleNamespace()
    result.client = client
    result.user = auth_user

    return result


@pytest.fixture
def image_file() -> callable:
    def create_image_file(filename='image.png'):
        image = create_image()
        return SimpleUploadedFile(filename, image.getvalue(), content_type='image/png')

    return create_image_file


@pytest.fixture
async def communicator():
    async def connector(path):
        _communicator = WebsocketCommunicator(application, path)
        connected, _ = await _communicator.connect()
        assert connected
        return _communicator

    return connector


@pytest.fixture
def client_session(client, settings):
    settings.SESSION_ENGINE = 'django.contrib.sessions.backends.file'
    engine = import_module(settings.SESSION_ENGINE)
    store = engine.SessionStore()
    store.save()
    session = store
    client.cookies[settings.SESSION_COOKIE_NAME] = store.session_key
    return session


def pytest_sessionfinish(session, exitstatus):
    shutil.rmtree(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'media/test'), ignore_errors=True)
