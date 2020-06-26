from django.urls import path

from . import views

app_name = 'common'
urlpatterns = [
    path('switch-language/', views.SwitchLanguageView.as_view(), name='switch_language'),
    path('services/', views.ServicesView.as_view(), name='services'),
    path('living-in-armenia/', views.LivingInKuwaitView.as_view(), name='living_in_armenia'),
    path('about-us/', views.AboutUsView.as_view(), name='about_us'),
    path('contact-us/', views.ContactUsView.as_view(), name='contact_us'),
    path('privacy-policy/', views.PrivacyPolicyView.as_view(), name='privacy_policy'),
    path('terms/', views.TermsView.as_view(), name='terms'),
    path('help-and-support/', views.HelpSupportView.as_view(), name='help_and_support'),
    path('subscribe/', views.SubscribeView.as_view(), name='subscribe'),
]
