from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken

from django.contrib.auth.password_validation import validate_password
from django.utils.six import text_type
from django.utils.translation import gettext_lazy as _

import core.utils
import users.services
import users.utils
from users.models import SocialConnection, User

__all__ = (
    'LoginSerializer',
    'SignupSerializer',
    'ConfirmEmailSerializer',
    'ForgotPasswordSerializer',
    'ResetPasswordSerializer',
    'SocialConnectSerializer',
)


class AuthPayload(object):

    @staticmethod
    def get_auth_payload(user: User, additional_data: dict = None) -> dict:

        def get_avatar(avatar):
            if avatar:
                return avatar.url

            return None

        refresh = RefreshToken.for_user(user)

        payload = {
            'user': {
                'pk': user.pk,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'avatar': get_avatar(user.avatar),
            },
            'refresh_token': text_type(refresh),
            'access_token': text_type(refresh.access_token),
        }

        if additional_data:
            payload = {**payload, **additional_data}

        return payload


# noinspection PyAbstractClass
class LoginSerializer(serializers.Serializer, AuthPayload):
    email = serializers.EmailField()
    password = serializers.CharField()

    def validate(self, validated_data):
        return self.get_auth_payload(self.get_user(**validated_data))

    @staticmethod
    def get_user(email: str, password: str) -> User:
        invalid_credentials = _('Invalid login credentials.')

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError(invalid_credentials)

        if not user.check_password(password):
            raise serializers.ValidationError(invalid_credentials)

        return user


class SignupSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(max_length=181)

    class Meta:
        model = User
        fields = ('email', 'password', 'full_name', 'phone_number', )

    @staticmethod
    def validate_password(value):
        validate_password(value)
        return value

    @staticmethod
    def validate_full_name(value):
        invalid_name_error_msg = _('Provided name is invalid.')
        try:
            first_name, last_name = (val.strip() for val in value.strip().split(' ', 1))
        except ValueError:
            raise serializers.ValidationError(invalid_name_error_msg)
        return first_name, last_name

    @staticmethod
    def validate_email(value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError(_('A user with this email address is already exists.'))
        return value

    def create(self, validated_data):
        first_name, last_name = validated_data['full_name']

        user = User(
            first_name=first_name,
            last_name=last_name,
            email=validated_data['email'],
            phone_number=validated_data['phone_number'],
            is_active=False,
            email_confirmation_token=User.generate_token(),
        )
        user.set_password(validated_data['password'])
        user.save()

        users.utils.emails.send_email_address_confirmation(user)

        return {'msg': _('Please confirm your email.')}


# noinspection PyAbstractClass
class ConfirmEmailSerializer(serializers.Serializer, AuthPayload):
    token = serializers.CharField()

    def validate_token(self, value):
        # noinspection PyAttributeOutsideInit
        self.user = User.objects.filter(email_confirmation_token=value).first()
        if not self.user:
            raise serializers.ValidationError(_('Invalid token.'))
        return value

    def create(self, validated_data):
        self.user.is_active = True
        self.user.email_confirmation_token = None
        self.user.save()

        return self.get_auth_payload(
            user=self.user,
            additional_data={
                'msg': _('You have successfully confirmed you email address.')
            },
        )


# noinspection PyAbstractClass
class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def create(self, validated_data):
        user = User.objects.filter(email=validated_data['email']).first()
        if user:
            user.generate_password_request_date()
            user.reset_password_token = User.generate_token()
            user.save()

            users.utils.emails.send_forgot_password_request(user)

        return {'msg': _('Please check your email.')}


# noinspection PyAbstractClass
class ResetPasswordSerializer(serializers.Serializer, AuthPayload):
    token = serializers.CharField()
    password = serializers.CharField()

    def validate_token(self, value):
        # noinspection PyAttributeOutsideInit
        self.user = User.objects.filter(reset_password_token=value).first()

        if not self.user:
            raise serializers.ValidationError(_('Invalid Reset Password Link.'))

        return value

    @staticmethod
    def validate_password(value):
        validate_password(value)
        return value

    def create(self, validated_data):
        self.user.reset_password_token = None
        self.user.reset_password_request_date = None
        self.user.is_active = True
        self.user.set_password(validated_data['password'])

        self.user.save()

        return self.get_auth_payload(self.user)


class SocialConnectSerializer(serializers.ModelSerializer, AuthPayload):
    access_token = serializers.CharField()
    access_token_secret = serializers.CharField(required=False)
    email = serializers.EmailField(required=False)

    class Meta:
        model = SocialConnection
        fields = ('provider', 'access_token', 'email', 'access_token_secret')

    def validate(self, validated_data):
        provider = validated_data['provider']
        retrieve_user = getattr(users.services, f'{provider}_retrieve_user', None)
        if not retrieve_user:
            raise serializers.ValidationError('Invalid provider specified!')

        if provider == 'twitter':
            user = retrieve_user(validated_data['access_token'], validated_data['access_token_secret'])
        else:
            user = retrieve_user(validated_data['access_token'])
        if 'error' in user:
            raise serializers.ValidationError(user['error'])

        self.social = SocialConnection.objects.filter(
            provider=provider, provider_id=user['provider_id'],
        ).select_related('user').first()

        user['email'] = user.get('email', validated_data.get('email'))

        if self.social:
            user['email'] = self.social.user.email

        if not user['email']:
            raise serializers.ValidationError('Please provide an email.')

        user['provider'] = provider
        return user

    def create(self, validated_data):
        provider = validated_data['provider']
        provider_id = validated_data['provider_id']

        if self.social is None:
            email = validated_data['email']
            user = User.objects.filter(email=email).first()
            if user is None:
                user = User.objects.create(
                    first_name=validated_data['first_name'],
                    last_name=validated_data['last_name'],
                    email=validated_data['email'],
                )

                avatar_url = validated_data['avatar_url']
                if avatar_url:
                    self.save_avatar(user, avatar_url)

            self.social = SocialConnection.objects.create(
                provider_id=provider_id,
                provider=provider,
                user=user,
            )

        return self.get_auth_payload(user=self.social.user)

    @staticmethod
    def save_avatar(user, avatar_url):
        file = core.utils.get_image_from_url(avatar_url)
        if file:

            filename = avatar_url.split('/')[-1]
            if not any(filter(lambda ext: ext in filename, ['.jpeg', '.jpg', '.png'])):
                filename = 'avatar.jpeg'

            filename = core.utils.get_file_path(user, filename)
            user.avatar.save(filename, file, save=True)
