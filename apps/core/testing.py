import types

from PIL import Image

from django.utils.six import BytesIO


def create_image(size: tuple = (100, 100), image_mode: str = 'RGB', image_format: str = 'PNG'):
    """
    Generate a test image
    """
    data = BytesIO()
    Image.new(image_mode, size).save(data, image_format)
    data.seek(0)
    return data


def response(status_code: int, content: any) -> types.SimpleNamespace:
    """
    Generate a simple response object
    :param status_code:
    :param content:
    :return: SimpleNamespace
    """
    obj = types.SimpleNamespace()
    obj.status_code = status_code
    obj.json = lambda: content
    obj.content = content

    return obj
