from rest_framework import generics, mixins, permissions, status
from rest_framework.response import Response

from django.http import Http404

import ads.models
import messaging.models
from messaging.mixins import ThreadMixin

from .serializers import *  # noqa

__all__ = (
    'SendMessageAPIView',
    'InboxAPIView',
    'InboxDetailView',
    'BlockThreadAPIView',
)


class SendMessageAPIView(ThreadMixin, generics.CreateAPIView):
    queryset = messaging.models.Message.objects.all()
    serializer_class = MessageSerializer
    permission_classes = (permissions.IsAuthenticated,)
    status_code = status.HTTP_201_CREATED

    def get_object(self, ad_id):
        ad = (
            ads.models.Ad.objects
            .filter(pk=ad_id)
            .exclude(user=self.request.user)
            .select_related('user')
            .first()
        )
        if not ad or not ad.user:
            raise Http404

        return ad

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        ad = self.get_object(serializer.validated_data['ad_id'])
        thread = self.get_or_create_thread(ad)
        response = serializer.save_message(
            thread=thread,
            sender=self.request.user,
            message=serializer.validated_data['message']
        )
        if response:
            self.status_code = status.HTTP_400_BAD_REQUEST

        return Response(response, status=self.status_code)


class InboxAPIView(generics.ListAPIView):
    queryset = messaging.models.Message.objects.all()
    serializer_class = InboxSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        user = self.request.user
        threads = messaging.models.Thread.objects.filter(users=user)
        queryset = (messaging.models.Message.objects
                    .filter(thread__pk__in=threads)
                    .distinct('thread')
                    .select_related('thread__ad')
                    .order_by('thread', '-sent_at'))

        return ads.models.AdImage.primary_image(queryset, outer_ref='thread__ad__pk')


class InboxDetailView(generics.ListAPIView):
    queryset = messaging.models.Message.objects.all()
    serializer_class = InboxDetailSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        thread_id = self.kwargs.get('thread')
        return (
            messaging.models.Message.objects
            .filter(thread=thread_id, thread__users__pk=self.request.user.pk)
            .select_related('sender')
            .order_by('-sent_at')
        )


class BlockThreadAPIView(mixins.UpdateModelMixin, generics.GenericAPIView):
    queryset = messaging.models.Thread.objects.all()
    serializer_class = BlockThreadSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_object(self, thread_id):
        return self.queryset.filter(pk=thread_id, users__pk=self.request.user.pk).first()

    def patch(self, request, *args, **kwargs):
        serializer = self.serializer_class(
            data=request.data
        )
        serializer.is_valid(raise_exception=True)
        thread = self.get_object(serializer.validated_data['thread'])

        if not thread:
            raise Http404

        response = serializer.block_thread(thread=thread)

        return Response(response)
