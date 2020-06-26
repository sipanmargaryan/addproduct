from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator

from django.urls import path

from messaging.api.utils import TokenAuthMiddlewareStack
from messaging.consumers import MessageConsumer

application = ProtocolTypeRouter({
    'websocket': AllowedHostsOriginValidator(
        TokenAuthMiddlewareStack(
            URLRouter(
                [
                    path('chat/<int:pk>/', MessageConsumer),
                ]
            )
        )
    )
})
