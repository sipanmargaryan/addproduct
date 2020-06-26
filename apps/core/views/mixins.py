import django.core.exceptions
from django.conf import settings
from django.contrib.auth.mixins import AccessMixin
from django.shortcuts import redirect

__all__ = (
    'AnonymousRequiredMixin',
    'LoginRedirectMixin',
    'MetaDescriptionViewMixin',
)


class AnonymousRequiredMixin(AccessMixin):
    """Verifies that request is anonymous."""
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('users:profile')
        return super().dispatch(request, *args, **kwargs)


class LoginRedirectMixin(AccessMixin):
    redirect_url = settings.LOGIN_REDIRECT_URL

    def get_redirect_url(self):
        redirect_url = self.request.GET.get(
            self.redirect_field_name,
            self.redirect_url,
        )
        return redirect_url


class MetaDescriptionViewMixin:
    """
    Provides ``meta_description`` variable to template context.
    """

    meta_description = None

    def get_meta_description(self):
        if self.meta_description is None:
            raise django.core.exceptions.ImproperlyConfigured('meta_description attribute is not specified.')
        return self.meta_description

    def get_context_data(self, **kwargs):
        kwargs['meta_description'] = self.get_meta_description()
        # noinspection PyUnresolvedReferences
        return super(MetaDescriptionViewMixin, self).get_context_data(**kwargs)
