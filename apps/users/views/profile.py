from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import generic

import users.forms
import users.models
from users.mixins import ProfileFormViewMixin

__all__ = (
    'ProfileView',
    'ContactInfoView',
    'ChangePasswordView',
    'NotificationSettingsView',
)


class ProfileView(LoginRequiredMixin, generic.TemplateView):
    template_name = 'profile/profile.html'

    def get_context_data(self, **kwargs):
        context = super(ProfileView, self).get_context_data(**kwargs)

        user = self.request.user
        if 'contact_info_form' not in context:
            user = self.request.user
            initial = dict(
                full_name=user.get_full_name(),
                email=user.email,
                phone_number=user.phone_number,
                city=user.city,
                avatar=user.get_avatar(),
            )
            context['contact_info_form'] = users.forms.ContactInfoForm(initial=initial)

        if 'change_password_form' not in context:
            context['change_password_form'] = users.forms.ChangePasswordForm(instance=user)

        if 'notification_form' not in context:
            context['notification_form'] = users.forms.NotificationForm(instance=user.notification)

        return context


class ContactInfoView(LoginRequiredMixin, ProfileFormViewMixin, generic.View):
    form_class = users.forms.ContactInfoForm


class ChangePasswordView(LoginRequiredMixin, ProfileFormViewMixin, generic.View):
    form_class = users.forms.ChangePasswordForm

    def after_save(self):
        update_session_auth_hash(self.request, self.request.user)


class NotificationSettingsView(LoginRequiredMixin, ProfileFormViewMixin, generic.View):
    form_class = users.forms.NotificationForm
