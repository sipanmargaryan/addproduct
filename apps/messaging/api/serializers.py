from rest_framework import serializers

from django.contrib.humanize.templatetags.humanize import naturaltime
from django.core.files import storage
from django.utils.translation import gettext as _

import messaging.models
from messaging.api.utils import Firebase

__all__ = (
    'MessageSerializer',
    'InboxSerializer',
    'InboxDetailSerializer',
    'BlockThreadSerializer',
)


class MessageSerializer(serializers.ModelSerializer):
    ad_id = serializers.IntegerField()

    class Meta:
        model = messaging.models.Message
        fields = ('message', 'ad_id')

    @staticmethod
    def save_message(thread, sender, message):

        if thread.blocked:
            return {
                'msg': 'Thread is blocked.'
            }

        messaging.models.Message.objects.create(
            thread=thread,
            message=message,
            sender=sender
        )

        data = {
            'message': message,
            'full_name': sender.get_full_name(),
            'avatar': sender.avatar.url if sender.avatar else '',
        }

        users = thread.users.all()
        registration_ids = [users[0].device_id, users[1].device_id]
        Firebase().send_message(data, registration_ids, 1)


class InboxSerializer(serializers.ModelSerializer):
    thread = serializers.SerializerMethodField()

    class Meta:
        model = messaging.models.Message
        fields = (
            'thread',
        )

    @staticmethod
    def get_thread(message):
        return {
            'pk': message.thread.pk,
            'ad_title': message.thread.ad.title,
            'message': message.message,
            'blocked': message.thread.blocked,
            'primary_image': storage.default_storage.url(message.primary_image),
            'sent_at': naturaltime(message.sent_at),
        }


class InboxDetailSerializer(serializers.ModelSerializer):
    sender = serializers.SerializerMethodField()
    sender_name = serializers.SerializerMethodField()

    class Meta:
        model = messaging.models.Message
        fields = (
            'pk', 'message', 'sent_at', 'sender', 'sender_name'
        )

    @staticmethod
    def get_sender(message):
        return message.sender.pk

    @staticmethod
    def get_sender_name(message):
        return message.sender.get_full_name()


class BlockThreadSerializer(serializers.ModelSerializer):
    thread = serializers.IntegerField(write_only=True)

    class Meta:
        model = messaging.models.Thread
        fields = ('thread', )

    @staticmethod
    def block_thread(thread):
        thread.blocked = True
        thread.save()

        return {
            'msg': _('Chat has been blocked.')
        }
