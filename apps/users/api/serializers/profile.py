from rest_framework import serializers

from django.contrib.auth.password_validation import validate_password
from django.utils.translation import gettext_lazy as _

import users.models
from core.api.serializers import CitySerializer

__all__ = (
    'UserProfileSerializer',
    'UserProfileUpdateSerializer',
    'ChangePasswordSerializer',
    'ChangeAvatarSerializer',
    'NotificationSerializer',
    'ChangeDeviceSerializer',
)


class UserProfileSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    is_password_specified = serializers.SerializerMethodField()
    city = CitySerializer()

    class Meta:
        model = users.models.User
        fields = (
            'pk',
            'phone_number',
            'email',
            'city',
            'avatar',
            'full_name',
            'device_id',
            'date_joined',
            'is_password_specified',
        )
        extra_kwargs = {
            'avatar': {
                'read_only': True
            }
        }

    @staticmethod
    def get_full_name(obj):
        return obj.get_full_name()

    @staticmethod
    def get_is_password_specified(obj):
        return bool(obj.password)


class UserProfileUpdateSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(write_only=True)

    class Meta:
        model = users.models.User
        fields = (
            'phone_number',
            'email',
            'city',
            'full_name',
        )

    def update(self, instance, validated_data):
        instance.email = self.value_or_none(validated_data, 'email')
        instance.phone_number = self.value_or_none(validated_data, 'phone_number')
        instance.city = self.value_or_none(validated_data, 'city')
        instance.first_name, instance.last_name = validated_data['full_name']
        instance.save()

        return instance

    # noinspection PyMethodMayBeStatic
    def validate_full_name(self, value):
        full_name = value
        try:
            first_name, last_name = (val.strip() for val in full_name.strip().split(' ', 1))
        except ValueError:
            raise serializers.ValidationError(_('Make sure you have first and last names included.'))
        return first_name, last_name

    @staticmethod
    def value_or_none(data, key):
        return data.get(key, None) or None


# noinspection PyAbstractClass
class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=False)
    new_password = serializers.CharField()

    def validate_old_password(self, value):
        if self.context['user'].password and not value:
            raise serializers.ValidationError(_('Old password is required.'))

        if not self.context['user'].check_password(value):
            raise serializers.ValidationError(_('Invalid password.'))

        return value

    def validate_new_password(self, value):
        validate_password(value, self.context['user'])
        return value

    @staticmethod
    def change_password(user, password):
        user.set_password(password)
        user.save()

        return {
            'msg': _('Your password updated.')
        }


# noinspection PyAbstractClass
class ChangeAvatarSerializer(serializers.ModelSerializer):
    class Meta:
        model = users.models.User
        fields = ('avatar',)


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = users.models.Notification
        fields = ('ad_answer', 'news_offer_promotion')


class ChangeDeviceSerializer(serializers.ModelSerializer):
    device_id = serializers.CharField(write_only=True)

    class Meta:
        model = users.models.User
        fields = ('device_id', )

    @staticmethod
    def change_device(user, device):
        user.device_id = device
        user.save()
