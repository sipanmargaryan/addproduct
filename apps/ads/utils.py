from django.conf import settings
from django.core.cache import cache

from core.email.utils import send_email
from core.utils.utils import build_client_absolute_url

__all__ = (
    'send_notify_me',
)


def send_notify_me(user, context):

    subject = 'New ads based on your search at {site_name}'.format(
        site_name=settings.SITE_NAME
    )

    send_email(
        subject=subject,
        template_name='emails/notify_me.html',
        context={
            'search_url': build_client_absolute_url(context['search_url']),
            'search_count': context['search_count'],
        },
        to=user.email,
    )


def get_kwd_usd_rate():
    return cache.get('kwd_usd_rate', 3.30)


def get_kwd_for_one_day():
    return 5
