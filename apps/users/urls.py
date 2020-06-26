from django.contrib.auth import views as auth_views
from django.urls import include, path

from . import views

auth_patterns = [
    path('login/', views.LoginView.as_view(), name='login'),
    path('signup/', views.SignupView.as_view(), name='signup'),
    path('signup/success/<str:email>/', views.SignupSuccessView.as_view(), name='signup_success'),
    path('confirm-email/<str:token>/', views.ConfirmEmailView.as_view(), name='confirm_email'),
    path('oauth/<str:provider>/', views.OAuthRedirectView.as_view(), name='oauth'),
    path('oauth-complete/<str:provider>/', views.OAuthCompleteView.as_view(), name='oauth_complete'),
    path('oauth-email/', views.OAuthEmailView.as_view(), name='oauth_email'),
    path('forgot-password/', views.ForgotPasswordView.as_view(), name='forgot_password'),
    path('forgot-password-success/', views.ForgotPasswordSuccessView.as_view(), name='forgot_password_success'),
    path('reset-password/<str:token>/', views.ResetPasswordView.as_view(), name='reset_password'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
]

profile_patterns = [
    path('', views.ProfileView.as_view(), name='profile'),
    path('contact-info/', views.ContactInfoView.as_view(), name='contact_info'),
    path('change-password/', views.ChangePasswordView.as_view(), name='change_password'),
    path('notification-settings/', views.NotificationSettingsView.as_view(), name='notification_settings'),
]

app_name = 'users'
urlpatterns = [
    path('', include(auth_patterns)),
    path('', include(profile_patterns)),
]
