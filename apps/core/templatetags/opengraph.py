from django import template
from django.conf import settings

register = template.Library()


@register.inclusion_tag('core/opengraph/meta.html')
def opengraph_meta(site_name=None, title=None, image=None, description=None):
    if hasattr(image, 'url'):
        image = image.url
    if not site_name:
        site_name = settings.SITE_NAME
    return {
        'site_name': site_name,
        'title': title,
        'image': image,
        'description': description,
    }
