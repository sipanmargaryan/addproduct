import json

import pytest

from django.urls import reverse

import core.testing
import payments.factories
import payments.utils
import users.factories
from core.utils import build_client_absolute_url


def test_create_token(monkeypatch, settings):

    token_data = {'id': 'charge_token_id'}
    card_info = {
        'number': 5123450000000008,
        'cvc': 124,
        'exp_year': 21,
        'exp_month': 12,
    }

    def response(url, payload, headers):
        payload = json.loads(payload)
        assert settings.KNET_API_KEY in headers['Authorization']
        assert payload['card']['number'] == card_info['number']
        assert payload['card']['cvc'] == card_info['cvc']
        assert payload['card']['exp_year'] == card_info['exp_year']
        assert payload['card']['exp_month'] == card_info['exp_month']
        return core.testing.response(200, token_data)

    monkeypatch.setattr('requests.post', response)
    charge = payments.utils.KNet().create_token(card_info)
    assert charge['id'] == token_data['id']


@pytest.mark.django_db
def test_charge(monkeypatch, settings):
    user = users.factories.UserFactory(phone_number='965-50000000')
    payment = payments.factories.PaymentFactory(user=user)
    token = '0' * 10
    charge_data = {
        'id': 'knet_charge_id',
        'transaction': {
            'url': 'https://api.knet/'
        }
    }

    def response(url, payload, headers):
        payload = json.loads(payload)
        assert settings.KNET_API_KEY in headers['Authorization']
        assert payload['amount'] == payment.cost
        assert payload['currency'] == payment.currency
        assert payload['source']['id'] == token if token else 'src_kw.knet'
        assert payload['customer']['first_name'] == payment.user.first_name
        assert payload['redirect']['url'] == build_client_absolute_url(reverse('payments:proceed'))
        return core.testing.response(200, charge_data)

    monkeypatch.setattr('requests.post', response)
    charge = payments.utils.KNet().charge(payment, user, token)
    assert charge['id'] == charge_data['id']
    assert charge['transaction']['url'] == charge_data['transaction']['url']

    token = ''
    charge = payments.utils.KNet().charge(payment, user, token)
    assert charge['id'] == charge_data['id']


def test_retrieve_charge(monkeypatch, settings):
    test_charge_id = 'knet_charge_id'
    retrieve_data = {'status': 'CAPTURED'}

    def response(url, headers):
        assert settings.KNET_API_KEY in headers['Authorization']
        assert url == f'https://api.tap.company/v2/charges/{test_charge_id}'
        return core.testing.response(200, retrieve_data)

    monkeypatch.setattr('requests.get', response)
    retrieve_charge = payments.utils.KNet().retrieve_charge(test_charge_id)

    assert retrieve_charge['status'] == retrieve_data['status']
