from django.urls import path

from .views import *  # noqa

app_name = 'payments'
urlpatterns = [
    path('payment/<int:pk>/', PaymentView.as_view(), name='payment'),
    path('card-charge/', CreditCardChargeView.as_view(), name='credit_charge'),
    path('knet-charge/', KnetChargeView.as_view(), name='knet_charge'),
    path('history/', PaymentHistoryView.as_view(), name='history'),
    path('knet-proceed/', KnetProceedView.as_view(), name='proceed'),
    path('payment-success/', PaymentSuccessView.as_view(), name='success'),
    path('payment-error/', PaymentErrorView.as_view(), name='error'),
]
