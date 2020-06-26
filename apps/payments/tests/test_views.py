import pytest

from django.urls import reverse

import payments.factories
import payments.models


@pytest.mark.django_db
def test_payment(logged_in):
    payment = payments.factories.PaymentFactory(
        user=logged_in.user,
    )

    response = logged_in.client.get(reverse('payments:payment', kwargs={'pk': payment.pk}))
    assert response.status_code == 200

    assert response.context['form'] is not None
    assert response.context['paypal_form'] is not None


@pytest.mark.django_db
def test_payment_invalid(logged_in):
    payment = payments.factories.PaymentFactory()

    response = logged_in.client.get(reverse('payments:payment', kwargs={'pk': payment.pk}))
    assert response.status_code == 404


@pytest.mark.django_db
def test_knet_charge(logged_in, monkeypatch):
    knet_charge_id = 'knet_charge_id'
    payment = payments.factories.PaymentFactory(
        user=logged_in.user,
    )
    payload = {'payment_id': payment.pk}

    # noinspection PyUnusedLocal
    def charge(self, payment, user):
        return {
            'id': knet_charge_id,
            'transaction': {
                'url': 'https://api.knet/'
            }
        }

    monkeypatch.setattr('payments.utils.KNet.charge', charge)
    response = logged_in.client.post(reverse('payments:knet_charge'), payload)
    payment.refresh_from_db()

    assert response.status_code == 200
    assert payment.knet_charge_id == knet_charge_id
    assert response.json()['url']


@pytest.mark.django_db
def test_knet_charge_invalid(logged_in):
    payment = payments.factories.PaymentFactory(
        user=logged_in.user,
    )
    payload = {'payment_id': 99}

    response = logged_in.client.post(reverse('payments:knet_charge'), payload)
    payment.refresh_from_db()

    assert response.status_code == 400
    assert payment.knet_charge_id is None


@pytest.mark.django_db
def test_credit_card_charge(logged_in, monkeypatch):
    knet_charge_id = 'knet_charge_id'
    payment = payments.factories.PaymentFactory(
        user=logged_in.user,
    )
    payload = {
        'payment_id': payment.pk,
        'number': 5123450000000008,
        'cvc': 124,
        'exp_year': 21,
        'exp_month': 12,
    }

    # noinspection PyUnusedLocal
    def create_token(*args, **kwargs):
        return {'id': 'charge_token_id'}

    # noinspection PyUnusedLocal
    def charge(*args, **kwargs):
        return {
            'id': knet_charge_id,
            'transaction': {
                'url': 'https://api.knet/'
            }
        }

    monkeypatch.setattr('payments.utils.KNet.create_token', create_token)
    monkeypatch.setattr('payments.utils.KNet.charge', charge)
    response = logged_in.client.post(reverse('payments:credit_charge'), payload)
    payment.refresh_from_db()

    assert response.status_code == 200
    assert response.json()['url']
    assert payment.knet_charge_id == knet_charge_id


@pytest.mark.django_db
def test_credit_card_charge_invalid(logged_in, monkeypatch):
    payment = payments.factories.PaymentFactory(
        user=logged_in.user,
    )
    payload = {
        'payment_id': payment.pk,
        'number': 5123450000000008,
        'cvc': 124,
        'exp_month': 12,
    }

    # noinspection PyUnusedLocal
    def create_token(*args, **kwargs):
        return {'id': ''}

    monkeypatch.setattr('payments.utils.KNet.create_token', create_token)

    response = logged_in.client.post(reverse('payments:credit_charge'), payload)
    assert response.status_code == 400

    payload['exp_year'] = 21

    response = logged_in.client.post(reverse('payments:credit_charge'), payload)
    assert response.status_code == 400


@pytest.mark.django_db
def test_payment_history(logged_in):
    payments_count = 10
    payments.factories.PaymentFactory.create_batch(payments_count, user=logged_in.user)
    payments.factories.PaymentFactory.create_batch(payments_count)

    response = logged_in.client.get(reverse('payments:history'))

    assert response.status_code == 200
    assert len(response.context['payments']) == payments_count


@pytest.mark.django_db
def test_payment_success(logged_in, monkeypatch):
    payment = payments.factories.PaymentFactory(
        knet_charge_id='knet_charge_id',
        user=logged_in.user,
    )
    payload = {'tap_id': payment.knet_charge_id}

    # noinspection PyUnusedLocal
    def retrieve_charge(*args, **kwargs):
        return {'status': 'CAPTURED'}

    monkeypatch.setattr('payments.utils.KNet.retrieve_charge', retrieve_charge)

    response = logged_in.client.get(reverse('payments:proceed'), payload)
    payment.refresh_from_db()

    assert response.status_code == 302
    assert payment.knet_charge_id is None
    assert payment.status == payments.models.Payment.PAID


@pytest.mark.django_db
def test_payment_success_invalid(logged_in):
    payment = payments.factories.PaymentFactory(
        knet_charge_id='knet_charge_id',
        user=logged_in.user,
    )
    payload = {'tap_id': 'invalid_knet_charge_id'}

    response = logged_in.client.get(reverse('payments:proceed'), payload)
    payment.refresh_from_db()

    assert response.status_code == 302
    assert payment.knet_charge_id
    assert payment.status == payments.models.Payment.PENDING

    payment = payments.factories.PaymentFactory(
        knet_charge_id='knet_charge_id',
    )
    response = logged_in.client.get(reverse('payments:proceed'), payload)
    payment.refresh_from_db()

    assert response.status_code == 302
    assert payment.knet_charge_id
    assert payment.status == payments.models.Payment.PENDING
