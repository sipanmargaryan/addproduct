from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import redirect
from django.urls import reverse
from django.views import generic

import faq.forms
import faq.models

__all__ = (
    'QuestionsView',
    'AskQuestionView',
    'QuestionDetailView',
    'ReportView',
)


class QuestionsView(generic.ListView):
    model = faq.models.Question
    paginate_by = 4
    top = True
    template_name = 'faq/questions.html'
    context_object_name = 'questions'

    def get_queryset(self):
        queryset = super(QuestionsView, self).get_queryset()

        search = self.request.GET.get('q')
        category = self.request.GET.getlist('category')

        if category:
            queryset = queryset.filter(category__pk__in=category)
        if search:
            queryset = queryset.filter(Q(title__icontains=search) | Q(description__icontains=search))

        if self.top:
            queryset = queryset.order_by('-answer_count')
        else:
            queryset = queryset.order_by('-created')

        return faq.models.Answer.attach_answer_count(queryset)

    def get_context_data(self, **kwargs):
        context = super(QuestionsView, self).get_context_data(**kwargs)
        context['category_questions'] = faq.models.Category.category_count()
        return context


class AskQuestionView(generic.CreateView):
    template_name = 'faq/ask.html'
    form_class = faq.forms.AskQuestionForm

    def form_valid(self, form):
        question = form.save(commit=False)
        question.category = faq.models.Category.objects.get(pk=form.cleaned_data['category'])
        question.save()

        return redirect(reverse('faq:top_questions'))


class QuestionDetailView(generic.FormView, generic.DetailView):
    form_class = faq.forms.AnswerForm
    queryset = faq.models.Question.objects.all()
    template_name = 'faq/question_detail.html'
    model = faq.models.Answer
    context_object_name = 'question'

    def get_queryset(self):
        return self.model.attach_answer_count(self.queryset)

    def get_context_data(self, **kwargs):
        context = super(QuestionDetailView, self).get_context_data(**kwargs)
        context['category_questions'] = faq.models.Category.category_count()
        context['other_questions'] = self.other_questions()
        return context

    def form_valid(self, form):
        question = self.object

        answer = form.save(commit=False)
        answer.question = question

        parent = form.cleaned_data['answer_id']
        if parent:
            answer.parent = self.model.objects.filter(pk=parent).first()

        answer.save()

        return redirect(reverse('faq:question_detail', kwargs={'pk': question.pk, 'slug': question.slug}))

    def post(self, request, *args, **kwargs):
        # noinspection PyAttributeOutsideInit
        self.object = self.get_object()
        return super().post(request, *args, **kwargs)

    def other_questions(self):
        questions = faq.models.Question.objects.exclude(pk=self.object.pk).order_by('-created')[:4]
        return self.model.attach_answer_count(questions)


class ReportView(LoginRequiredMixin, generic.DetailView):
    model = faq.models.Answer

    # noinspection PyUnusedLocal
    def post(self, request, *args, **kwargs):
        self.get_object().reports.create(user=request.user)
        return HttpResponse(status=204)
