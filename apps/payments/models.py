from django_extensions.db.models import TimeStampedModel

from django.contrib.auth import get_user_model
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext as _

import ads.models

__all__ = (
    'Payment',
)


class Payment(TimeStampedModel):
    CREDIT = 'CC'
    PAYPAL = 'PP'
    KNET = 'KN'
    METHODS = (
        (CREDIT, _('Credit Card')),
        (PAYPAL, _('Paypal')),
        (KNET, _('KNET')),
    )

    ADVERTISEMENT_AD = 'advertisement ad'
    TYPES = (
        (ADVERTISEMENT_AD, _('advertisement ad')),
    )

    PENDING = 'pending'
    PAID = 'paid'
    STATUS = (
        (PENDING, _('pending')),
        (PAID, _('paid')),
    )

    CURRENCIES = (
        ('KWD', 'KWD'),
        ('USD', 'USD'),
    )

    cost = models.FloatField()
    premium_days = models.IntegerField(default=0)
    method = models.CharField(max_length=10, choices=METHODS, default=None, null=True)
    payment_type = models.CharField(max_length=20, choices=TYPES, default=ADVERTISEMENT_AD)
    currency = models.CharField(max_length=3, choices=CURRENCIES, default='KWD')
    status = models.CharField(max_length=7, choices=STATUS, default=PENDING)
    knet_charge_id = models.CharField(max_length=256, null=True)

    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    ad = models.ForeignKey(ads.models.Ad, on_delete=models.CASCADE)

    def get_absolute_url(self):
        url = reverse('payments:payment', kwargs={'pk': self.pk})
        if self.status == self.PAID:
            url = reverse('payments:success')
        return url

    def __str__(self):
        return f'{self.method} - {self.cost} {self.currency}'
