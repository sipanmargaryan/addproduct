from rest_framework_simplejwt.views import TokenRefreshView

from django.urls import include, path

from .views import auth, profile

auth_patterns = [
    path('login/', auth.LogInAPIView.as_view(), name='login'),
    path('signup/', auth.SignupAPIView.as_view(), name='signup'),
    path('confirm-email/', auth.ConfirmEmailAPIView.as_view(), name='confirm_email_address'),
    path('forgot-password/', auth.ForgotPasswordAPIView.as_view(), name='forgot_password'),
    path('reset-password/', auth.ResetPasswordAPIView.as_view(), name='reset_password'),
    path('refresh-token/', TokenRefreshView.as_view()),
    path('social-connect/', auth.SocialConnectAPIView.as_view(), name='social_connect'),
]

profile_patterns = [
    path('change-password/', profile.ChangePasswordAPIView.as_view(), name='change_password'),
    path(
        'change-avatar/',
        profile.ChangeAvatarViewSet.as_view({
            'post': 'update',
        }),
        name='change_avatar'
    ),
    path(
        'profile-info/',
        profile.ProfileViewSet.as_view({
            'get': 'retrieve',
            'put': 'update',
        }),
        name="profile"
    ),
    path(
        'change-notification/',
        profile.ChangeNotificationViewSet.as_view({
            'get': 'retrieve',
            'put': 'update',
        }),
        name='notification'
    ),
    path('connect-device/', profile.ConnectDeviceAPIView.as_view(), name='connect_device'),
]

app_name = 'accounts_api'
urlpatterns = [
    path('', include(auth_patterns)),
    path('', include(profile_patterns)),
]
