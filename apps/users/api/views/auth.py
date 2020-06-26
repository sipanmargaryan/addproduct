from rest_framework import status
from rest_framework.generics import GenericAPIView

from users.api.mixins import SaveSerializerMixin

from ..serializers import *  # noqa

__all__ = (
    'LogInAPIView',
    'SignupAPIView',
    'ConfirmEmailAPIView',
    'ForgotPasswordAPIView',
    'ResetPasswordAPIView',
)


class LogInAPIView(GenericAPIView, SaveSerializerMixin):
    """
    JWT authentication endpoint
    """
    serializer_class = LoginSerializer
    save = False


class SignupAPIView(GenericAPIView, SaveSerializerMixin):
    status_code = status.HTTP_201_CREATED
    serializer_class = SignupSerializer


class ConfirmEmailAPIView(GenericAPIView, SaveSerializerMixin):
    serializer_class = ConfirmEmailSerializer


class ForgotPasswordAPIView(GenericAPIView, SaveSerializerMixin):
    serializer_class = ForgotPasswordSerializer


class ResetPasswordAPIView(GenericAPIView, SaveSerializerMixin):
    serializer_class = ResetPasswordSerializer


class SocialConnectAPIView(GenericAPIView, SaveSerializerMixin):
    serializer_class = SocialConnectSerializer
