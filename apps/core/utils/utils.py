import uuid
from typing import Optional

import requests

from django.conf import settings
from django.core.files import File
from django.core.files.temp import NamedTemporaryFile
from django.db.models import IntegerField, Subquery
from django.utils.text import slugify
from django.utils.translation import gettext as _

__all__ = (
    'get_file_path',
    'build_client_absolute_url',
    'get_image_from_url',
    'Array',
    'SubqueryCount',
    'RequiredAttrMeta',
    'get_required_error_msg',
)


def get_file_path(instance, filename: str) -> str:
    model = type(instance)
    upload_dir = '{}/{}'.format(
        slugify(model._meta.app_label),
        slugify(model.__name__)
    )

    upload_dir = upload_dir.replace('ad', 'classified')
    ext = filename.split('.')[-1]
    filename = '{}.{}'.format(uuid.uuid4(), ext)
    return 'images/{}/{}'.format(upload_dir, filename)


def build_client_absolute_url(path: str) -> str:
    domain = settings.CLIENT_DOMAIN
    url_scheme = settings.URL_SCHEME

    return '{url_scheme}://{domain}{path}'.format(
        url_scheme=url_scheme,
        domain=domain,
        path=path,
    )


def get_image_from_url(url: str) -> Optional[File]:
    response = requests.get(url)

    if response.status_code == 200:

        img_temp = NamedTemporaryFile(delete=True)
        img_temp.write(response.content)
        img_temp.flush()

        return File(img_temp)


class Array(Subquery):
    template = 'ARRAY(%(subquery)s)'


class SubqueryCount(Subquery):
    template = '(SELECT count(*) FROM (%(subquery)s) _count)'
    output_field = IntegerField()


class RequiredAttrMeta(type):
    def __init__(cls, name, bases, clsdict):
        super().__init__(name, bases, clsdict)
        if not bases:
            return
        if not hasattr(cls, '_required_attributes'):
            return
        for attr in cls._required_attributes:
            if not hasattr(cls, attr):
                raise AttributeError(f'Attribute {attr} not present in {name}')


def get_required_error_msg():
    return _('This field is required')
