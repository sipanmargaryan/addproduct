from django import forms
from django.contrib.auth import get_user_model
from django.utils.translation import gettext as _

import users.models

__all__ = (
    'ContactInfoForm',
    'ChangePasswordForm',
    'NotificationForm',
)


class ContactInfoForm(forms.ModelForm):
    full_name = forms.CharField()

    class Meta:
        model = users.models.User
        fields = ('full_name', 'email', 'phone_number', 'city', 'avatar', )

    def clean_full_name(self) -> tuple:
        full_name = self.cleaned_data['full_name']
        try:
            first_name, last_name = (val.strip() for val in full_name.strip().split(' ', 1))
        except ValueError:
            raise forms.ValidationError(_('Make sure you have first and last names included.'))
        return first_name, last_name

    def save(self, commit=True):
        user = super().save(commit=False)

        user.first_name, user.last_name = self.cleaned_data['full_name']
        if commit:
            user.save()

        return user


class ChangePasswordForm(forms.ModelForm):

    old_password = forms.CharField(
        label=_('Current password'),
        strip=False,
        widget=forms.PasswordInput(),
    )

    password = forms.CharField(
        label=_('New password'),
        strip=False,
        widget=forms.PasswordInput(),
    )
    password_confirmation = forms.CharField(
        label=_('Confirm new Password'),
        strip=False,
        widget=forms.PasswordInput(),
    )

    def __init__(self, *args, **kwargs):
        super(ChangePasswordForm, self).__init__(*args, **kwargs)

        instance = kwargs.get('instance')
        if not instance.password:
            self.fields['old_password'].required = False
            self.fields['old_password'].widget.attrs['readonly'] = True
            self.fields['old_password'].widget.attrs['disabled'] = True

    class Meta:
        model = get_user_model()
        fields = ('old_password', 'password', 'password_confirmation')

    def clean_old_password(self):
        old_password = self.cleaned_data['old_password']

        if self.instance.password and not self.instance.check_password(old_password):
            raise forms.ValidationError(_('Current password is incorrect.'))

    def clean_password_confirmation(self):
        password = self.cleaned_data['password']
        password_confirmation = self.cleaned_data['password_confirmation']

        if password and password_confirmation and password != password_confirmation:
            raise forms.ValidationError(_('Passwords didn\'t match.'))

    def save(self, commit=True):
        user = super().save(commit)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()

        return user


class NotificationForm(forms.ModelForm):

    CHOICE_OPTIONS = {
        'coerce': lambda choice: choice == 'yes',
        'choices': (('no', 'No'), ('yes', 'Yes')),
        'widget': forms.RadioSelect,
    }

    ad_answer = forms.TypedChoiceField(**CHOICE_OPTIONS)
    news_offer_promotion = forms.TypedChoiceField(**CHOICE_OPTIONS)

    def __init__(self, *args, **kwargs):
        instance = kwargs.get('instance')
        if instance and isinstance(instance, users.models.User):
            kwargs['instance'] = instance.notification
        super(NotificationForm, self).__init__(*args, **kwargs)

    class Meta:
        model = users.models.Notification
        exclude = ('user', )
