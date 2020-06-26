from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import OuterRef, Prefetch, Subquery
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.utils.translation import gettext_lazy as _
from django.views import generic

import ads.models
import messaging.models
import users.models

from .mixins import ThreadMixin

__all__ = (
    'InboxView',
    'InboxDetailView',
    'BlockThreadView',
    'SendMessageView',
    'GoToThreadView',
)


class InboxView(generic.TemplateView):
    model = messaging.models.Message
    template_name = 'messaging/inbox.html'

    def get_threads(self, user):
        threads = messaging.models.Thread.objects.filter(users=user)
        members = Prefetch('thread__users', users.models.User.objects.exclude(pk=user.pk))

        return (
            self.model.objects
                .filter(thread__pk__in=threads)
                .distinct('thread')
                .select_related('thread__ad')
                .prefetch_related(members)
                .order_by('thread', '-sent_at')
        )

    def get_context_data(self, **kwargs):
        context = super(InboxView, self).get_context_data(**kwargs)
        context['threads'] = self.get_threads(self.request.user)

        return context


class InboxDetailView(generic.TemplateView):
    model = messaging.models.Thread
    template_name = 'messaging/inbox_detail.html'

    def get_thread_details(self, thread_id, user):
        user = users.models.User.objects.filter(pk__in=OuterRef('users')).exclude(pk=user.pk)
        messages = Prefetch(
            'message_set',
            queryset=messaging.models.Message.objects.exclude(message=messaging.models.Message.HIDDEN_MESSAGE),
            to_attr='messages'
        )

        queryset = (
            self.model.objects
                .filter(pk=thread_id)
                .annotate(name=Subquery(user.values('first_name')[:1]))
                .exclude(name=None)
                .select_related('ad')
                .prefetch_related(messages)
        )

        queryset = ads.models.AdImage.primary_image(queryset, outer_ref='ad__pk')
        return queryset.first()

    def get_context_data(self, **kwargs):
        context = super(InboxDetailView, self).get_context_data(**kwargs)

        thread = self.get_thread_details(
            thread_id=self.kwargs.get('pk'),
            user=self.request.user,
        )

        if not thread:
            raise Http404

        context['thread'] = thread
        return context


class BlockThreadView(LoginRequiredMixin, generic.View):
    model = messaging.models.Thread

    # noinspection PyUnusedLocal
    def post(self, request, *args, **kwargs):
        thread_id = request.POST.get('thread_id')
        thread = self.model.objects.filter(pk=thread_id, users=request.user).first()

        if not thread:
            raise Http404

        thread.blocked = True
        thread.save()
        return HttpResponse(status=204)


class SendMessageView(LoginRequiredMixin, ThreadMixin, generic.View):

    # noinspection PyUnusedLocal
    def post(self, request, *args, **kwargs):

        message = request.POST.get('message')
        if not message:
            return HttpResponse(_('Invalid message.'), status=400)

        ad_id = request.POST.get('ad_id')
        ad = (
            ads.models.Ad.objects
            .filter(pk=ad_id)
            .exclude(user=request.user)
            .select_related('user')
            .first()
        )
        if not ad or not ad.user:
            raise Http404

        thread = self.get_or_create_thread(ad)
        if thread.blocked:
            return HttpResponse(_('Thread is blocked.'), status=400)

        messaging.models.Message.objects.create(
            thread=thread,
            message=message,
            sender=request.user,
        )

        return HttpResponseRedirect(thread.get_absolute_url())


class GoToThreadView(LoginRequiredMixin, ThreadMixin, generic.RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        ad_id = kwargs.get('pk')

        ad = (
            ads.models.Ad.objects
            .filter(pk=ad_id)
            .exclude(user=self.request.user)
            .select_related('user')
            .first()
        )
        if not ad or not ad.user:
            raise Http404

        thread = self.get_or_create_thread(ad)
        if thread.blocked:
            return HttpResponse(_('Thread is blocked.'), status=400)

        messaging.models.Message.objects.create(
            thread=thread,
            message=messaging.models.Message.HIDDEN_MESSAGE,
            sender=self.request.user,
        )

        return thread.get_absolute_url()
