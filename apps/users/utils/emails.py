from django.conf import settings
from django.urls import reverse

from core.email.utils import send_email
from core.utils.utils import build_client_absolute_url

__all__ = (
    'send_email_address_confirmation',
    'send_forgot_password_request',
)


def send_email_address_confirmation(user):
    email_confirmation_path = reverse('users:confirm_email', kwargs={'token': user.email_confirmation_token})

    subject = 'Confirm your registration at {site_name}'.format(
        site_name=settings.SITE_NAME
    )

    send_email(
        subject=subject,
        template_name='emails/email_address_confirmation.html',
        context={
            'email_confirmation_url': build_client_absolute_url(email_confirmation_path),
        },
        to=user.email,
    )


def send_forgot_password_request(user):
    reset_password_path = reverse('users:reset_password', kwargs={'token': user.reset_password_token})

    subject = 'Reset your {site_name} password'.format(
        site_name=settings.SITE_NAME
    )

    send_email(
        subject=subject,
        template_name='emails/forgot_password_request.html',
        context={
            'reset_password_url': build_client_absolute_url(reset_password_path),
        },
        to=user.email,
    )
