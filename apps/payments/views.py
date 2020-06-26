from paypal.standard.forms import PayPalPaymentsForm

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse, JsonResponse
from django.urls import reverse
from django.utils import timezone
from django.views import generic

import ads.models
import payments.forms
import payments.models
import payments.utils

__all__ = (
    'PaymentView',
    'KnetChargeView',
    'CreditCardChargeView',
    'PaymentHistoryView',
    'KnetProceedView',
    'PaymentSuccessView',
    'PaymentErrorView',
)


class PaymentView(LoginRequiredMixin, generic.DetailView):
    model = payments.models.Payment
    template_name = 'payments/payment.html'
    context_object_name = 'payment'

    def get_queryset(self):
        queryset = super(PaymentView, self).get_queryset()
        return queryset.filter(
            user=self.request.user,
            status=self.model.PENDING,
        )

    def get_context_data(self, **kwargs):
        context = super(PaymentView, self).get_context_data(**kwargs)
        standard = payments.utils.get_payment_info(self.get_object())
        context['form'] = payments.forms.CreditCardForm()
        context['paypal_form'] = PayPalPaymentsForm(initial=standard)
        return context


class KnetChargeView(LoginRequiredMixin, generic.View):
    model = payments.models.Payment

    def get_payment(self):
        queryset = self.model.objects.filter(
            pk=self.request.POST.get('payment_id'),
            user=self.request.user,
        )

        return queryset.first()

    # noinspection PyUnusedLocal
    def post(self, request, *args, **kwargs):
        payment = self.get_payment()

        if not payment:
            return HttpResponse(status=400)

        charge = payments.utils.KNet().charge(payment, request.user)

        payment.knet_charge_id = charge['id']
        payment.method = self.model.KNET
        payment.save()

        return JsonResponse({'url': charge['transaction']['url']})


class CreditCardChargeView(LoginRequiredMixin, generic.View):
    model = payments.models.Payment
    form_class = payments.forms.CreditCardForm

    def get_payment(self):
        queryset = self.model.objects.filter(
            pk=self.request.POST.get('payment_id'),
            user=self.request.user,
        )

        return queryset.first()

    # noinspection PyUnusedLocal
    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if not form.is_valid():
            return JsonResponse(form.errors, status=400)

        payment = self.get_payment()

        knet = payments.utils.KNet()
        token = knet.create_token(form.cleaned_data)
        token_id = token.get('id')

        if not token_id or not payment:
            return HttpResponse(status=400)

        charge = knet.charge(payment, request.user, token_id)
        payment.knet_charge_id = charge['id']
        payment.method = self.model.CREDIT
        payment.save()

        return JsonResponse({'url': charge['transaction']['url']})


class PaymentHistoryView(LoginRequiredMixin, generic.ListView):
    queryset = payments.models.Payment.objects.all()
    paginate_by = None
    template_name = 'payments/history.html'
    context_object_name = 'payments'

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user).order_by('-modified')


class KnetProceedView(LoginRequiredMixin, generic.RedirectView):
    model = payments.models.Payment

    def get_payment(self):
        knet_charge_id = self.request.GET.get('tap_id')
        if not knet_charge_id:
            return None

        queryset = self.model.objects.filter(
            knet_charge_id=knet_charge_id,
            user=self.request.user,
        )

        return queryset.first()

    def get_redirect_url(self, **kwargs):

        payment = self.get_payment()
        if not payment:
            return reverse('payments:error')

        charge = payments.utils.KNet().retrieve_charge(payment.knet_charge_id)
        if charge['status'] == 'CAPTURED':
            payment.knet_charge_id = None
            payment.status = self.model.PAID
            payment.save()

            ad = ads.models.Ad.objects.get(pk=payment.ad.pk)
            premium_until_date = ad.premium_until and ad.premium_until or timezone.now()
            ad.premium_until = premium_until_date + timezone.timedelta(days=payment.premium_days)
            ad.save()

        return reverse('payments:success')


class PaymentSuccessView(LoginRequiredMixin, generic.TemplateView):
    template_name = 'payments/success.html'


class PaymentErrorView(LoginRequiredMixin, generic.TemplateView):
    template_name = 'payments/error.html'
