from django.core.files import File

from core.testing import response
from core.utils import get_image_from_url


def test_get_image_from_url(monkeypatch):
    monkeypatch.setattr('requests.get', lambda url: response(200, b'image_data'))
    image = get_image_from_url('test')
    image.seek(0)

    assert type(image) is File
    assert image.read() == b'image_data'

    monkeypatch.setattr('requests.get', lambda url: response(400, None))
    assert get_image_from_url('test') is None
