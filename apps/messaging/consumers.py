import json

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer

import messaging.models
from messaging.api.utils import Firebase


class MessageConsumer(AsyncWebsocketConsumer):

    async def websocket_connect(self, event):

        self.user = self.retrieve_user()
        if self.user.is_anonymous:
            await self.close()
        self.thread = self.scope['url_route']['kwargs']['pk']
        self.thread_room = f'thread_{self.thread}'

        await self.channel_layer.group_add(
            self.thread_room,
            self.channel_name
        )
        await self.accept()

    async def websocket_receive(self, event):
        message_text = event.get('text', None)
        data = json.loads(message_text)
        if data['message']:
            message = await self.save_message(data['message'])
            send_data = dict(
                message=data['message'],
                sender=message.sender.pk,
                pk=message.pk,
                sender_name=message.sender.get_full_name(),
                sent_at=message.sent_at.__str__(),
            )
            await self.firebase_notification(message)
            await self.channel_layer.group_send(
                self.thread_room,
                {
                    'type': 'new_message',
                    'data': json.dumps(send_data),
                }
            )

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.thread_room,
            self.channel_name
        )

    async def new_message(self, event):
        await self.send(text_data=event['data'])

    async def firebase_notification(self, message):
        firebase_data = dict(
            message=message.message,
            thread_id=message.thread.pk,
            full_name=self.user.get_full_name(),
            avatar=self.user.avatar.url if self.user.avatar else '',
        )
        users = message.thread.users.all()
        user = users[1].device_id if users[0].device_id == self.user.pk else users[0].device_id
        registration_ids = [user]
        await Firebase().send_message(firebase_data, registration_ids, 1)

    def retrieve_user(self):
        return self.scope['user']

    @database_sync_to_async
    def save_message(self, message):
        thread = messaging.models.Thread.objects.get(pk=self.thread, blocked=False)
        return messaging.models.Message.objects.create(
            thread=thread,
            sender=self.user,
            message=message,
        )
