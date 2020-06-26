from django.urls import path

from .views import *  # noqa

app_name = 'messaging_api'
urlpatterns = [
    path('send-message/', SendMessageAPIView.as_view(), name='send_message'),
    path('inbox/', InboxAPIView.as_view(), name='inbox'),
    path('inbox/<int:thread>/', InboxDetailView.as_view(), name='inbox_detail'),
    path('block/', BlockThreadAPIView.as_view(), name='block_thread'),
]
