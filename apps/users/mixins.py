from typing import Optional

from django.http import HttpResponse, JsonResponse

import core.utils
import users.models


class SocialAuthMixin(object):
    @staticmethod
    def set_social_user(authentication_data: dict) -> Optional[users.models.User]:
        """
        Create new User and SocialConnection based on social data.
        :param authentication_data:
        :return: User
        """
        email = authentication_data.get('email')

        if not email:
            return

        user = users.models.User(
            email=authentication_data['email'],
            first_name=authentication_data['first_name'],
            last_name=authentication_data['last_name'],
        )

        if authentication_data.get('confirm_email'):
            user.email_confirmation_token = user.generate_token()

        user.set_avatar(authentication_data['avatar_url'])
        user.save()

        users.models.SocialConnection.objects.create(
            provider=authentication_data['provider'],
            provider_id=authentication_data['provider_id'],
            user=user,
        )
        return user


class ProfileFormViewMixin(metaclass=core.utils.RequiredAttrMeta):
    _required_attributes = ['form_class']

    # noinspection PyMethodMayBeStatic, PyUnusedLocal
    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST, request.FILES or None, instance=request.user)
        if form.is_valid():
            form.save()

            after_save = getattr(self, 'after_save', None)
            if after_save and callable(after_save):
                after_save()

            return HttpResponse(status=204)
        else:
            return JsonResponse(form.errors, status=400)
