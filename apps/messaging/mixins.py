import messaging.models


class ThreadMixin(object):

    def get_or_create_thread(self, ad):
        user = self.request.user

        thread = messaging.models.Thread.objects.filter(ad=ad, users=user).prefetch_related('users').first()
        if not thread:
            thread = messaging.models.Thread.objects.create(ad=ad)
            thread.users.set([user, ad.user])

        return thread
