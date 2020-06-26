from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect
from django.views import generic

import blog.forms
import blog.models

__all__ = (
    'VoteCommentView',
    'ReportView',
    'NewComment',
)


class VoteCommentView(LoginRequiredMixin, generic.View):
    model = blog.models.Comment

    # noinspection PyMethodMayBeStatic
    def post(self, request, *args, **kwargs):
        vote_type = request.POST.get('vote_type', blog.models.Vote.LIKE)
        comment = self.model.objects.get(pk=request.POST.get('comment_id'))
        vote, _ = blog.models.Vote.objects.get_or_create(
            comment=comment,
            user=request.user
        )
        if vote.vote_type != vote_type:
            vote.vote_type = vote_type
            vote.save()
        else:
            vote.delete()

        output_data = dict(
            like_count=comment.likes(),
            dislike_count=comment.dislikes(),
        )
        return JsonResponse(output_data)


class ReportView(LoginRequiredMixin, generic.DetailView):
    model = blog.models.Comment

    # noinspection PyUnusedLocal
    def post(self, request, *args, **kwargs):
        self.get_object().reports.create(user=request.user)
        return HttpResponse(status=204)


class NewComment(LoginRequiredMixin, generic.FormView):
    form_class = blog.forms.CommentForm

    def form_valid(self, form):
        article = blog.models.Article.objects.filter(pk=form.cleaned_data['article_id']).first()

        comment = form.save(commit=False)
        comment.user = self.request.user
        comment.article = article

        parent = form.cleaned_data['comment_id']
        if parent:
            comment.parent = blog.models.Comment.objects.filter(pk=parent).first()

        comment.save()

        return redirect(article.get_absolute_url())

    # noinspection PyMethodMayBeStatic
    def form_invalid(self, form):
        return JsonResponse(form.errors, status=400)
