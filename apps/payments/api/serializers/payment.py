from rest_framework import serializers

from django.utils import timezone
from django.utils.translation import gettext_lazy as _

import ads.models
import payments.models
import payments.utils

__all__ = (
    'PaymentHistorySerializer',
    'PaymentSerializer',
    'CreditCardSerializer',
    'UpdatePaymentStatusSerializer',
)


class PaymentHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = payments.models.Payment
        fields = (
            'pk',
            'payment_type',
            'method',
            'cost',
            'created'
        )


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = payments.models.Payment
        fields = (
            'pk',
            'payment_type',
            'method',
            'cost',
            'created'
        )


class CreditCardSerializer(serializers.Serializer):
    payment_id = serializers.IntegerField()
    exp_month = serializers.CharField()
    exp_year = serializers.CharField()
    cvc = serializers.CharField(min_length=3, max_length=4)
    number = serializers.CharField(min_length=12, max_length=19)

    def charge(self, payment_info, data):
        token_id = self.create_token(data)

        if not token_id:
            return {
                'msg': _('Invalid Card Credentials.')
            }

        knet = payments.utils.KNet()
        charge = knet.charge(payment_info, self.context['request'].user, token_id)
        payment_info.knet_charge_id = charge['id']
        payment_info.method = payments.models.Payment.CREDIT
        payment_info.save()

        return {
            'url': charge['transaction']['url']
        }

    @staticmethod
    def create_token(data):
        knet = payments.utils.KNet()
        token = knet.create_token(data)
        return token.get('id')


class UpdatePaymentStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = payments.models.Payment
        fields = ('knet_charge_id', )

    @staticmethod
    def change_paid(payment):
        charge = payments.utils.KNet().retrieve_charge(payment.knet_charge_id)
        if charge['status'] == 'CAPTURED':
            payment.knet_charge_id = None
            payment.status = payments.models.Payment.PAID
            payment.save()
            ad = ads.models.Ad.objects.get(pk=payment.ad.pk)
            premium_until_date = ad.premium_until and ad.premium_until or timezone.now()
            ad.premium_until = premium_until_date + timezone.timedelta(days=payment.premium_days)
            ad.save()
            return {
                'msg': _('Your Payment has been successfully proceed')
            }
