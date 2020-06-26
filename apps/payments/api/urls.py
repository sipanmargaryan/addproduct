from django.urls import path

from .views import *  # noqa

app_name = 'payments_api'
urlpatterns = [
    path('payments-history/', PaymentHistoryAPIView.as_view(), name='history'),
    path('knet-charge/<int:pk>/', KnetChargeAPIView.as_view(), name='knet_charge'),
    path('paypal-charge/<int:pk>/', PaypalAPIView.as_view(), name='paypal_charge'),
    path('credit-charge/', CreditCardChargeAPIView.as_view(), name='credit_charge'),
    path('knet-proceed/', KnetProceedAPIView.as_view(), name='proceed'),
]
