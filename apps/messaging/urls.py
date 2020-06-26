from django.urls import path

from .views import *  # noqa

app_name = 'messaging'
urlpatterns = [
    path('inbox/', InboxView.as_view(), name='inbox'),
    path('inbox/<int:pk>/', InboxDetailView.as_view(), name='inbox_detail'),
    path('block/', BlockThreadView.as_view(), name='block_thread'),
    path('send-message/', SendMessageView.as_view(), name='send_message'),
    path('go-to-thread/<int:pk>/', GoToThreadView.as_view(), name='go_to_thread'),
]
