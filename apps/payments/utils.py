import calendar
import json
import uuid

import requests

from django.conf import settings
from django.urls import reverse
from django.utils import timezone

from ads.utils import get_kwd_usd_rate
from core.utils import build_client_absolute_url

__all__ = (
    'get_payment_info',
    'KNet',
    'months',
    'years',
)


def get_payment_info(payment):
    return {
        'business': settings.PAYPAL_RECEIVER_EMAIL,
        'amount': payment.cost * get_kwd_usd_rate(),
        'item_name': payment.ad.title,
        'currency_code': 'USD',
        'invoice': f'{payment.pk}-{uuid.uuid4()}',
        'notify_url': build_client_absolute_url(reverse('paypal-ipn')),
        'return': build_client_absolute_url(reverse('payments:success')),
        'cancel_return': build_client_absolute_url(reverse('payments:error')),
        'custom': payment.pk,
    }


class KNet(object):

    def __init__(self):
        self.headers = {
            'content-type': 'application/json',
            'Authorization': f'Bearer {settings.KNET_API_KEY}'
        }
        self.token_url = 'https://api.tap.company/v2/tokens'
        self.charge_url = 'https://api.tap.company/v2/charges'

    def create_token(self, card_info):
        payload = {
            'card': card_info
        }
        response = requests.post(self.token_url, json.dumps(payload), headers=self.headers)
        return response.json()

    def charge(self, payment, user, token=None):
        country_code, _, phone_number = user.phone_number.partition('-')

        currency_code = payment.currency
        if not token:
            token = 'src_kw.knet'
            currency_code = 'KWD'

        payload = {
            'amount': payment.cost,
            'currency': currency_code,
            'customer': {
                'first_name': user.first_name,
                'last_name': user.last_name,
                'email': user.email,
                'phone': {
                    'country_code': country_code,
                    'number': phone_number,
                }
            },
            'source': {
                'id': token,
            },
            'redirect': {
                'url': build_client_absolute_url(reverse('payments:proceed')),
            }
        }

        response = requests.post(self.charge_url, json.dumps(payload), headers=self.headers)
        return response.json()

    def retrieve_charge(self, charge_id):
        retrieve_charge_url = f'{self.charge_url}/{charge_id}'
        response = requests.get(retrieve_charge_url, headers=self.headers)
        return response.json()


def months():
    return [(f'0{key}'[-2:], value) for key, value in enumerate(calendar.month_name) if value]


def years():
    current_year = timezone.now().year
    return [(str(year)[2:], year) for year in range(current_year, current_year + 10)]
