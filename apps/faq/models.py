from django_extensions.db import fields
from mptt.models import MPTTModel, TreeForeignKey

from django.contrib.contenttypes.fields import GenericRelation
from django.db import models
from django.db.models import Count, OuterRef
from django.urls import reverse_lazy
from django.utils import timezone

import core.models
import core.utils

__all__ = (
    'Category',
    'Question',
    'Answer',
)


class AbstractArticle(models.Model):
    author_full_name = models.CharField(max_length=256)
    author_email = models.EmailField()
    description = models.TextField()
    created = models.DateField(default=timezone.now)

    class Meta:
        abstract = True


class Category(core.models.AbstractCategory):
    class Meta:
        verbose_name_plural = 'FAQ Categories'

    @classmethod
    def category_count(cls):
        return cls.objects.values('pk', 'name').annotate(count=Count('question'))


class Question(AbstractArticle):
    title = models.CharField(max_length=256, unique=True)
    slug = fields.AutoSlugField(populate_from='title', blank=False)
    category = models.ForeignKey(Category, null=True, on_delete=models.SET_NULL)

    class Meta:
        unique_together = ('title', 'author_email')

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse_lazy('faq:question_detail', kwargs={'pk': self.pk, 'slug': self.slug})


class Answer(MPTTModel, AbstractArticle):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    parent = TreeForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='reply')
    reports = GenericRelation(core.models.Report, related_query_name='answers')

    def __str__(self):
        return self.description

    @classmethod
    def attach_answer_count(cls, queryset, outer_ref='pk'):
        answers = cls.objects.filter(question=OuterRef(outer_ref)).only('pk')
        return queryset.annotate(answer_count=core.utils.SubqueryCount(answers))
