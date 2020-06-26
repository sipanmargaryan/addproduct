from rest_framework import parsers, permissions, viewsets
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response

import users.models
from users.api.mixins import MultiSerializerViewSetMixin

from ..serializers import *  # noqa

__all__ = (
    'ProfileViewSet',
    'ChangePasswordAPIView',
    'ChangeAvatarViewSet',
    'ChangeNotificationViewSet',
    'ConnectDeviceAPIView',
)


class ProfileViewSet(MultiSerializerViewSetMixin, viewsets.ModelViewSet):
    queryset = users.models.User.objects.all()
    serializer_action_classes = {
        'retrieve': UserProfileSerializer,
        'update': UserProfileUpdateSerializer,
    }
    permission_classes = (permissions.IsAuthenticated,)

    def get_object(self):
        return self.request.user


class ChangePasswordAPIView(GenericAPIView):
    serializer_class = ChangePasswordSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_object(self):
        return self.request.user

    def patch(self, request, *args, **kwargs):
        serializer = self.serializer_class(
            data=request.data,
            context=dict(
                user=self.get_object()
            )
        )

        serializer.is_valid(raise_exception=True)
        response = serializer.change_password(
            user=self.get_object(),
            password=serializer.validated_data['new_password'],
        )

        return Response(response)


class ChangeAvatarViewSet(viewsets.ModelViewSet):
    queryset = users.models.User.objects.all()
    serializer_class = ChangeAvatarSerializer
    permission_classes = (permissions.IsAuthenticated,)
    parser_classes = (parsers.MultiPartParser,)

    def get_object(self):
        return self.queryset.filter(pk=self.request.user.pk).first()


class ChangeNotificationViewSet(viewsets.ModelViewSet):
    queryset = users.models.Notification.objects.all()
    serializer_class = NotificationSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_object(self):
        return self.queryset.filter(user=self.request.user).first()


class ConnectDeviceAPIView(GenericAPIView):
    queryset = users.models.User.objects.all()
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = ChangeDeviceSerializer

    def patch(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        response = serializer.change_device(
            user=self.request.user,
            device=serializer.validated_data['device_id'],
        )

        return Response(response)
