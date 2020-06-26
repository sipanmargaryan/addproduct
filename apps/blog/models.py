from ckeditor_uploader.fields import RichTextUploadingField
from django_extensions.db import fields
from django_extensions.db.models import ActivatorModel, TimeStampedModel
from mptt.models import MPTTModel, TreeForeignKey

from django.contrib.contenttypes.fields import GenericRelation
from django.db import models
from django.db.models import OuterRef
from django.urls import reverse

import core.models
import users.models
from core.utils import get_file_path

__all__ = (
    'Category',
    'Article',
    'Comment',
    'Vote',
)


class Category(core.models.AbstractCategory):
    class Meta:
        verbose_name_plural = 'Blog Categories'


class Article(ActivatorModel, TimeStampedModel):
    title = models.CharField(max_length=256, unique=True)
    slug = fields.AutoSlugField(populate_from='title', blank=False)
    description = RichTextUploadingField()
    hit_count = models.IntegerField(default=0)
    cover = models.ImageField(upload_to=get_file_path)

    category = models.ForeignKey(Category, related_name='category', on_delete=models.CASCADE)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('blog:article_detail', kwargs={'pk': self.pk, 'slug': self.slug})

    @classmethod
    def latest_news(cls, limit):
        return cls.objects.order_by('-created')[:limit]

    @classmethod
    def as_choices(cls):
        return cls.objects.values_list('pk', 'title')


class Comment(MPTTModel, TimeStampedModel):

    description = models.TextField()

    user = models.ForeignKey(users.models.User, related_name='user', on_delete=models.CASCADE)
    article = models.ForeignKey(Article, related_name='comments', on_delete=models.CASCADE)
    parent = TreeForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='reply')
    reports = GenericRelation(core.models.Report, related_query_name='comments')

    def report_url(self):
        return reverse('blog:report', kwargs={'pk': self.pk})

    def likes(self):
        return self.votes.filter(vote_type=Vote.LIKE).count()

    def dislikes(self):
        return self.votes.filter(vote_type=Vote.DISLIKE).count()

    @classmethod
    def attach_comment_count(cls, queryset, outer_ref='pk'):
        comments = cls.objects.filter(article=OuterRef(outer_ref)).only('pk')
        return queryset.annotate(comment_count=core.utils.SubqueryCount(comments))


class Vote(TimeStampedModel):
    LIKE = 'like'
    DISLIKE = 'dislike'

    VOTES = (
        (DISLIKE, 'dislike'),
        (LIKE, 'like')
    )

    vote_type = models.CharField(max_length=7, choices=VOTES)

    user = models.ForeignKey(users.models.User, on_delete=models.CASCADE)
    comment = models.ForeignKey(Comment, related_name='votes', on_delete=models.CASCADE)
