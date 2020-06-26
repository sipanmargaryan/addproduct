from django.contrib.auth import get_user_model
from django.db import models
from django.urls import reverse

import ads.models

__all__ = (
    'Thread',
    'Message',
)


class Thread(models.Model):

    blocked = models.BooleanField(default=False)

    ad = models.ForeignKey(ads.models.Ad, on_delete=models.CASCADE)
    users = models.ManyToManyField(get_user_model())

    def __str__(self):
        return f'{self.ad.title} - Chat'

    def get_absolute_url(self):
        return reverse('messaging:inbox_detail', kwargs={'pk': self.pk})

    @property
    def chat_url(self):
        if not self.pk:
            raise ValueError('pk is None')

        return f'/chat/{self.pk}/'


class Message(models.Model):
    HIDDEN_MESSAGE = str()

    message = models.TextField()
    unread = models.BooleanField(default=True)
    sent_at = models.DateTimeField(auto_now_add=True)

    thread = models.ForeignKey(Thread, on_delete=models.CASCADE)
    sender = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)

    def __str__(self):
        return self.message
