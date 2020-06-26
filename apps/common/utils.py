from django.conf import settings
from django.utils.translation import gettext as _

from core.email.utils import send_email


def send_contact_us(context):

    send_email(
        subject=_('Contact US'),
        template_name='emails/contact_us.html',
        context=context,
        to=settings.ADMIN_EMAIL,
    )
