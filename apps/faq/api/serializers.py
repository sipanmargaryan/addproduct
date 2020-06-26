from rest_framework import serializers

from django.utils.translation import gettext_lazy as _

import faq.models

__all__ = (
    'CategorySerializer',
    'QuestionSerializer',
    'QuestionDetailSerializer',
    'AskQuestionSerializer',
    'ReportSerializer',
    'AnswerSerializer',
)


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = faq.models.Category
        fields = ('pk', 'name')


class QuestionSerializer(serializers.ModelSerializer):
    answer_count = serializers.IntegerField()

    class Meta:
        model = faq.models.Question
        fields = ('pk', 'title', 'answer_count')


class QuestionDetailSerializer(serializers.ModelSerializer):
    answer_count = serializers.IntegerField()
    category = CategorySerializer()
    answers = serializers.SerializerMethodField()

    class Meta:
        model = faq.models.Question
        fields = (
            'pk',
            'title',
            'description',
            'category',
            'author_full_name',
            'author_email',
            'created',
            'answer_count',
            'answers',
        )

    @staticmethod
    def get_answers(question):
        queryset = faq.models.Answer.objects.filter(question=question.pk)
        return queryset.values('pk', 'description', 'author_full_name', 'author_email', 'created', 'parent')


class AskQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = faq.models.Question
        fields = (
            'title',
            'description',
            'category',
            'author_full_name',
            'author_email',
        )


class ReportSerializer(serializers.ModelSerializer):

    class Meta:
        model = faq.models.Answer
        fields = ('reports', )


class AnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = faq.models.Answer
        fields = (
            'question',
            'parent',
            'author_full_name',
            'author_email',
            'description',
        )

    # noinspection PyMethodMayBeStatic
    def validate_author_full_name(self, value):
        full_name = value
        try:
            assert len(val.strip() for val in full_name.strip().split(' ', 1)) == 2
        except AssertionError:
            raise serializers.ValidationError(_('Make sure you have first and last names included.'))
        return full_name
