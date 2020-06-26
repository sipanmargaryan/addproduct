from mailchimp3 import MailChimp

from django.conf import settings
from django.db.models import Count, Q
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect
from django.utils import translation
from django.views import generic

import common.forms
import common.models
import events.models
import faq.models

__all__ = (
    'SwitchLanguageView',
    'AboutUsView',
    'ContactUsView',
    'PrivacyPolicyView',
    'TermsView',
    'HelpSupportView',
    'SubscribeView',
    'ServicesView',
    'LivingInKuwaitView',
)


class SwitchLanguageView(generic.RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        language_code = self.request.GET.get('code', 'en')
        if language_code in [l[0] for l in settings.LANGUAGES]:
            translation.activate(language_code)
            self.request.session[translation.LANGUAGE_SESSION_KEY] = language_code

        return self.request.META.get('HTTP_REFERER', '/')


class AboutUsView(generic.TemplateView):
    template_name = 'common/about_us.html'


class ContactUsView(generic.FormView):
    template_name = 'common/contact_us.html'
    form_class = common.forms.ContactUsForm

    def form_valid(self, form):
        form.send_contact_email()
        return redirect('common:contact_us')


class PrivacyPolicyView(generic.TemplateView):
    template_name = 'common/privacy_policy.html'


class TermsView(generic.TemplateView):
    template_name = 'common/terms.html'


class HelpSupportView(generic.TemplateView):
    template_name = 'common/help.html'

    def get_context_data(self, **kwargs):
        context = super(HelpSupportView, self).get_context_data(**kwargs)
        search = self.request.GET.get('q', None)
        articles = common.models.Article.objects.all()
        if search:
            articles = articles.filter(Q(title__icontains=search) | Q(description__icontains=search))
        context['articles'] = articles
        return context


class SubscribeView(generic.View):
    form_class = common.forms.SubscriptionForm

    # noinspection PyMethodMayBeStatic, PyUnusedLocal
    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if not form.is_valid():
            return JsonResponse(form.errors, status=400)

        self.connect_to_mailchimp(form.cleaned_data['email'])
        return HttpResponse(status=204)

    def connect_to_mailchimp(self, email):
        first_name, last_name = ('', '')
        user = self.request.user
        if user.is_authenticated:
            first_name, last_name = (user.first_name, user.last_name)
        client = MailChimp(mc_api=settings.MAILCHIMP_API_KEY)
        try:
            client.lists.members.create(settings.MAILCHIMP_LIST_ID, {
                'email_address': email,
                'status': 'subscribed',
                'merge_fields': {
                    'FNAME': first_name,
                    'LNAME': last_name,
                },
            })
        except: pass  # noqa


class ServicesView(generic.ListView):
    queryset = common.models.Service.objects.all()
    paginate_by = None
    template_name = 'common/services.html'
    context_object_name = 'services'

    def get_queryset(self):
        queryset = self.queryset

        categories = self.request.GET.getlist('category')
        if categories:
            queryset = queryset.filter(category__name__in=categories)

        return queryset

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(ServicesView, self).get_context_data(**kwargs)
        context['categories'] = self.categories()
        context['count'] = self.queryset.count()
        return context

    def categories(self):
        categories = (
            common.models.Category.objects
            .annotate(service_count=Count('service'))
            .exclude(service_count=0)
        )

        selected = self.request.GET.getlist('category')
        if selected:
            for category in categories:
                if category.name in selected:
                    setattr(category, 'selected', True)

        return categories


class LivingInKuwaitView(generic.TemplateView):
    template_name = 'common/living_in_kuwait.html'

    def get_context_data(self, **kwargs):
        context = super(LivingInKuwaitView, self).get_context_data(**kwargs)

        context['questions'] = list(faq.models.Answer.attach_answer_count(
            faq.models.Question.objects.order_by('-created')
        )[:5])

        context['services'] = list(common.models.Service.objects.all()[:6])

        n = (len(context['questions']) + len(context['services'])) // 2
        context['events'] = events.models.Event.objects.select_related('city', 'category').order_by('-start_date')[:n]

        return context
