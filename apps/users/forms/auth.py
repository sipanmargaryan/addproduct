from django import forms
from django.contrib.auth import get_user_model, password_validation
from django.utils.translation import gettext as _

from core.utils.utils import get_required_error_msg

required_error_msg = get_required_error_msg()


class LoginForm(forms.Form):

    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'placeholder': _('Email')}),
    )
    password = forms.CharField(
        strip=False,
        widget=forms.PasswordInput(attrs={'placeholder': _('Password')}),
    )

    class Meta:
        error_messages = {
            'email': {
                'required': required_error_msg,
                'invalid': _('Enter a valid email address'),
            },
            'password': {
                'required': required_error_msg,
            }
        }

    def clean(self):
        cleaned_data = super().clean()
        error_messages = {'invalid_credentials': _('Invalid login credentials.')}

        email = cleaned_data.get('email')
        password = cleaned_data.get('password')

        if email and password:

            user = get_user_model().objects.filter(email=email).first()

            if not user or not user.check_password(password):
                raise forms.ValidationError(error_messages['invalid_credentials'])

            return user


class SignupForm(forms.ModelForm):
    full_name = forms.CharField(widget=forms.TextInput(attrs={'placeholder': _('First & Last name')}))

    class Meta:
        model = get_user_model()
        fields = ('full_name', 'email', 'password', 'phone_number', )
        widgets = {
            'email': forms.EmailInput(attrs={'placeholder': _('Email')}),
            'phone_number': forms.TextInput(attrs={'placeholder': _('Phone Number')}),
            'password': forms.PasswordInput(attrs={'placeholder': _('Password')}),
        }
        error_messages = {
            'full_name': {
                'required': required_error_msg,
            },
            'email': {
                'required': required_error_msg,
                'invalid': _('Enter a valid email address'),
            },
            'phone_number': {
                'required': required_error_msg,
            },
            'password': {
                'required': required_error_msg,
            },
        }

    def clean_full_name(self) -> tuple:
        full_name = self.cleaned_data['full_name']
        try:
            first_name, last_name = (val.strip() for val in full_name.strip().split(' ', 1))
        except ValueError:
            raise forms.ValidationError(_('Make sure you have first and last names included.'))
        return first_name, last_name

    def clean_password(self):
        password = self.cleaned_data['password']
        self.instance.email = self.cleaned_data.get('email')
        password_validation.validate_password(password, self.instance)

        return password

    def save(self, commit=True):
        user = super().save(commit=False)

        user.first_name, user.last_name = self.cleaned_data['full_name']
        user.set_password(self.cleaned_data['password'])
        user.email_confirmation_token = user.generate_token()
        user.is_active = False
        if commit:
            user.save()

        return user


class ForgotPasswordForm(forms.Form):
    email = forms.EmailField(widget=forms.EmailInput(attrs={'placeholder': _('Email')}))

    class Meta:
        error_messages = {
            'email': {
                'required': required_error_msg,
                'invalid': _('Enter a valid email address'),
            },
        }

    def set_token(self):
        user = get_user_model().objects.filter(email=self.cleaned_data['email']).first()

        if user:
            user.reset_password_token = user.generate_token()
            user.save()

        return user


class ResetPasswordForm(forms.Form):
    password = forms.CharField(widget=forms.PasswordInput)
    password_confirmation = forms.CharField(widget=forms.PasswordInput)

    def clean(self):
        password1 = self.cleaned_data.get('password')
        password2 = self.cleaned_data.get('password_confirmation')

        if password1 and password2 and password1 != password2:
            raise forms.ValidationError(_('Passwords didn\'t match.'))

        password_validation.validate_password(password1)

        return self.cleaned_data

    def change_password(self, token: str):
        user = get_user_model().objects.filter(reset_password_token=token).first()

        if user:
            user.reset_password_token = None
            user.set_password(self.cleaned_data['password'])
            user.save()

        return user


class EmailSignupForm(forms.Form):
    email = forms.EmailField(widget=forms.EmailInput(attrs={'placeholder': _('Email')}))

    class Meta:
        error_messages = {
            'email': {
                'required': required_error_msg,
                'invalid': _('Enter a valid email address'),
            },
        }

    def clean(self):
        user = get_user_model().objects.filter(email=self.cleaned_data['email']).first()
        if user:
            raise forms.ValidationError(_('User with this email address already exist.'))

        return self.cleaned_data
