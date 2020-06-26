from django import forms
from django.utils.functional import lazy
from django.utils.translation import gettext as _

import payments.utils

__all__ = (
    'CreditCardForm',
)


class CreditCardForm(forms.Form):

    exp_month = forms.ChoiceField(
        label=_('Expiration'),
        choices=lazy(payments.utils.months, tuple),
        widget=forms.Select(),
        required=True
    )
    exp_year = forms.ChoiceField(
        label=_('Year'),
        choices=lazy(payments.utils.years, tuple),
        widget=forms.Select(),
        required=True
    )
    cvc = forms.CharField(label='CVC/CVV', min_length=3, max_length=4)
    number = forms.CharField(label=_('Credit card number'), min_length=12, max_length=19)
