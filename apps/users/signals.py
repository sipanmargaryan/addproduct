from django.db.models.signals import post_save
from django.dispatch import receiver

import users.models


@receiver(post_save, sender=users.models.User)
def create_user_notifications(sender, instance, created, **kwargs):
    if created:
        users.models.Notification.objects.create(user=instance)
