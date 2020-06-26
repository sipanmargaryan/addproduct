from django import template

register = template.Library()


@register.simple_tag
def utcisoformat(event_date):
    return event_date.strftime('%Y%m%dT%H%M%SZ')
