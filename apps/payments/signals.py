from paypal.standard.ipn.signals import valid_ipn_received
from paypal.standard.models import ST_PP_COMPLETED

from django.conf import settings
from django.utils import timezone

import ads.models
from payments.models import Payment


def payment_process(sender, **kwargs):
    ipn_obj = sender
    payment = Payment.objects.filter(pk=ipn_obj.custom).first()
    if not payment:
        return
    if ipn_obj.payment_status == ST_PP_COMPLETED:
        if ipn_obj.receiver_email == settings.PAYPAL_RECEIVER_EMAIL:
            if ipn_obj.mc_gross == payment.cost:
                payment.status = Payment.PAID
                payment.method = Payment.PAYPAL
                payment.save()

                ad = ads.models.Ad.objects.get(pk=payment.ad.pk)
                premium_until_date = ad.premium_until and ad.premium_until or timezone.now()
                ad.premium_until = premium_until_date + timezone.timedelta(days=payment.premium_days)
                ad.save()


valid_ipn_received.connect(payment_process)
