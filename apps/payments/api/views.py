from rest_framework import generics, mixins, permissions, status
from rest_framework.response import Response

from django.http import Http404

import payments.models
import payments.utils

from .serializers import *  # noqa

__all__ = (
    'PaymentHistoryAPIView',
    'KnetChargeAPIView',
    'CreditCardChargeAPIView',
    'KnetProceedAPIView',
    'PaypalAPIView',
)


class PaymentHistoryAPIView(generics.ListAPIView):
    queryset = payments.models.Payment.objects.all()
    serializer_class = PaymentHistorySerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_object(self):
        return self.queryset.filter(user=self.request.user)


class KnetChargeAPIView(generics.RetrieveAPIView):
    queryset = payments.models.Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        payment_info = self.get_object()
        charge = payments.utils.KNet().charge(payment_info, request.user)

        payment_info.knet_charge_id = charge['id']
        payment_info.method = payments.models.Payment.KNET
        payment_info.save()
        return Response({'url': charge['transaction']['url']})


class CreditCardChargeAPIView(generics.GenericAPIView):
    queryset = payments.models.Payment.objects.all()
    serializer_class = CreditCardSerializer
    permission_classes = (permissions.IsAuthenticated,)
    status_code = status.HTTP_200_OK

    def get_payment(self, payment_id):
        try:
            return payments.models.Payment.objects.get(pk=payment_id, user=self.request.user)
        except payments.models.Payment.DoesNotExist:
            raise Http404

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        payment_info = self.get_payment(serializer.validated_data['payment_id'])
        response = serializer.charge(payment_info, serializer.validated_data)
        if response.get('msg'):
            self.status_code = status.HTTP_400_BAD_REQUEST
        return Response(response, status=self.status_code)


class KnetProceedAPIView(mixins.UpdateModelMixin, generics.GenericAPIView):
    queryset = payments.models.Payment.objects.all()
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = UpdatePaymentStatusSerializer

    def get_payment(self, knet_charge_id):
        return self.queryset.filter(
            knet_charge_id=knet_charge_id,
            user=self.request.user,
        ).first()

    def patch(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        payment = self.get_payment(serializer.validated_data['knet_charge_id'])

        if not payment:
            raise Http404

        response = serializer.change_paid(payment)

        return Response(response)


class PaypalAPIView(generics.RetrieveAPIView):
    queryset = payments.models.Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        payment_info = payments.utils.get_payment_info(self.get_object())
        return Response(payment_info)
