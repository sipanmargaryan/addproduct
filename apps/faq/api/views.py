from django_filters import rest_framework as filters
from rest_framework import generics, permissions, status
from rest_framework.response import Response

import faq.models
from faq.api.filters import QuestionFilter

from .serializers import *  # noqa

__all__ = (
    'QuestionsAPIView',
    'QuestionDetailAPIView',
    'AskQuestionAPIView',
    'ReportAPIView',
    'NewCommentAPIView',
    'CategoriesAPIView',
)


class QuestionsAPIView(generics.ListAPIView):
    queryset = faq.models.Question.objects.all()
    serializer_class = QuestionSerializer

    filter_backends = (filters.DjangoFilterBackend,)
    filter_class = QuestionFilter

    def get_queryset(self):
        queryset = faq.models.Answer.attach_answer_count(self.queryset)
        return queryset.order_by('-answer_count')


class QuestionDetailAPIView(generics.RetrieveAPIView):
    queryset = faq.models.Question.objects.all()
    serializer_class = QuestionDetailSerializer

    def get_queryset(self):
        return faq.models.Answer.attach_answer_count(self.queryset)

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)


class AskQuestionAPIView(generics.CreateAPIView):
    serializer_class = AskQuestionSerializer


class ReportAPIView(generics.CreateAPIView):
    queryset = faq.models.Answer.objects.all()
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = ReportSerializer

    def post(self, request, *args, **kwargs):
        self.get_object().reports.create(user=request.user)
        return Response(status=status.HTTP_204_NO_CONTENT)


class NewCommentAPIView(generics.CreateAPIView):
    queryset = faq.models.Answer.objects.all()
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = AnswerSerializer


class CategoriesAPIView(generics.ListAPIView):
    queryset = faq.models.Category.objects.all()
    serializer_class = CategorySerializer
