from typing import Optional

import django.contrib.auth
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views import generic

import users.forms
import users.mixins
import users.models
import users.utils
from core.views.mixins import AnonymousRequiredMixin, LoginRedirectMixin

__all__ = (
    'LoginView',
    'SignupView',
    'SignupSuccessView',
    'ConfirmEmailView',
    'OAuthRedirectView',
    'OAuthCompleteView',
    'OAuthEmailView',
    'ForgotPasswordView',
    'ForgotPasswordSuccessView',
    'ResetPasswordView',
)


class LoginView(AnonymousRequiredMixin, LoginRedirectMixin, generic.FormView):
    template_name = 'auth/login.html'
    form_class = users.forms.LoginForm

    def form_valid(self, form):
        user = form.cleaned_data
        django.contrib.auth.login(self.request, user)
        return HttpResponseRedirect(self.get_redirect_url())


class SignupView(AnonymousRequiredMixin, generic.CreateView):
    template_name = 'auth/signup.html'
    form_class = users.forms.SignupForm

    def get_success_url(self):
        return reverse_lazy('users:signup_success', kwargs={'email': self.object.email})

    def form_valid(self, form):
        response = super().form_valid(form)
        users.utils.send_email_address_confirmation(self.object)
        return response


class SignupSuccessView(AnonymousRequiredMixin, generic.TemplateView):
    template_name = 'auth/signup_success.html'

    def get_context_data(self, **kwargs):
        context = super(SignupSuccessView, self).get_context_data(**kwargs)
        context['email_address'] = kwargs.pop('email')
        return context


class ConfirmEmailView(LoginRedirectMixin, generic.View):
    queryset = users.models.User.objects.all()

    # noinspection PyUnusedLocal
    def get(self, request, *args, **kwargs):
        token = kwargs.pop('token')
        if not token:
            raise Http404

        user = self.queryset.filter(email_confirmation_token=token).first()
        if not user:
            raise Http404

        user.is_active = True
        user.email_confirmation_token = None
        user.save()
        django.contrib.auth.login(request, user)
        return HttpResponseRedirect(self.get_redirect_url())


class OAuthRedirectView(generic.View):
    def get(self, request, *args, **kwargs):
        builder = users.utils.SocialTokenRequestURIBuilder()
        token_request_uri = builder.build_token_request_uri(kwargs.pop('provider'))
        if token_request_uri:
            return redirect(token_request_uri)
        else:
            raise Http404


class OAuthCompleteView(users.mixins.SocialAuthMixin, LoginRedirectMixin, generic.View):
    def get(self, request, *args, **kwargs):
        provider = kwargs.pop('provider')

        authentication_data = self.parse_auth_code(provider)

        if not authentication_data:
            return redirect('users:login')

        authentication_data['provider'] = provider
        user = self.get_social_user(authentication_data)

        if not user:
            user = self.set_social_user(authentication_data)
            if not user:
                authentication_data.pop('email')
                self.request.session['authentication_data'] = authentication_data
                return redirect(reverse_lazy('users:oauth_email'))

        django.contrib.auth.login(self.request, user)
        return HttpResponseRedirect(self.get_redirect_url())

    def parse_auth_code(self, provider: str):
        code = self.request.GET.get('code')
        oauth_token = self.request.GET.get('oauth_token')
        oauth_verifier = self.request.GET.get('oauth_verifier')
        authentication_data = users.utils.SocialUserRetriever().retrieve_user(
            provider=provider, code=code,
            oauth_token=oauth_token,
            oauth_verifier=oauth_verifier,
        )

        return authentication_data

    @staticmethod
    def get_social_user(authentication_data: dict) -> Optional[users.models.User]:
        connection = users.models.SocialConnection.objects.filter(
            provider=authentication_data['provider'],
            provider_id=authentication_data['provider_id'],
        ).select_related('user').first()

        if connection:
            return connection.user

        if not authentication_data['email']:
            return

        user = users.models.User.objects.filter(email=authentication_data['email']).first()
        if user:
            users.models.SocialConnection.objects.create(
                provider=authentication_data['provider'],
                provider_id=authentication_data['provider_id'],
                user=user,
            )
        return user


class OAuthEmailView(AnonymousRequiredMixin, users.mixins.SocialAuthMixin, generic.FormView):
    template_name = 'auth/oauth_email.html'
    form_class = users.forms.EmailSignupForm

    def form_valid(self, form):
        user = self.signup_user(form.cleaned_data['email'])

        if user:
            users.utils.send_email_address_confirmation(user)
            return redirect(reverse_lazy('users:signup_success', kwargs={'email': user.email}))

        return redirect('users:login')

    def signup_user(self, email: str):
        authentication_data = self.request.session.get('authentication_data')
        keys = {'first_name', 'last_name', 'provider', 'provider_id', 'avatar_url'}

        if isinstance(authentication_data, dict) and keys == authentication_data.keys():
            authentication_data['email'] = email
            authentication_data['confirm_email'] = True
            user = self.set_social_user(authentication_data)
            users.utils.send_email_address_confirmation(user)
            return user


class ForgotPasswordView(AnonymousRequiredMixin, generic.FormView):
    template_name = 'auth/forgot_password.html'
    form_class = users.forms.ForgotPasswordForm

    def form_valid(self, form):
        user = form.set_token()

        if user:
            users.utils.send_forgot_password_request(user)
            self.request.session['email_address'] = user.email
            self.request.session.save()

        return redirect('users:forgot_password_success')


class ForgotPasswordSuccessView(generic.TemplateView):
    template_name = 'auth/forgot_password_success.html'

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        context_data['email_address'] = self.request.session.get('email_address')
        return context_data


class ResetPasswordView(LoginRedirectMixin, generic.FormView):
    template_name = 'auth/reset_password.html'
    form_class = users.forms.ResetPasswordForm
    queryset = users.models.User.objects.all()

    def dispatch(self, request, *args, **kwargs):
        token = kwargs.get('token')
        if not token:
            raise Http404

        user = self.queryset.filter(reset_password_token=token).first()
        if not user:
            raise Http404

        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        token = self.kwargs.get('token')
        user = form.change_password(token)
        if user:
            django.contrib.auth.login(self.request, user)

        return HttpResponseRedirect(self.get_redirect_url())
