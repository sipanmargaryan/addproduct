import re

from django import template
from django.conf import settings

register = template.Library()


@register.filter
def custom_range(number, arg=0):
    return range(arg, number)


@register.filter
def subtract(value, arg):
    return value - int(arg)


@register.simple_tag(takes_context=True)
def param_replace(context, **kwargs):
    d = context['request'].GET.copy()
    for k, v in kwargs.items():
        d[k] = v
    for k in [k for k, v in d.items() if not v]:
        del d[k]
    return d.urlencode()


@register.simple_tag
def active(request, pattern):
    if re.search(pattern, request.path):
        return 'active'
    return str()


@register.filter
def index(items, i):
    if len(items) > i:
        return items[i]


@register.simple_tag
def get_setting(name):
    return getattr(settings, name, '')


@register.filter
def to_class_name(value):
    return value.__class__.__name__
