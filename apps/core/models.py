from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models


class City(models.Model):
    name = models.CharField(max_length=256, unique=True)

    class Meta:
        ordering = ['name']
        verbose_name_plural = 'Cities'

    def __str__(self):
        return self.name

    @classmethod
    def as_choices(cls):
        return cls.objects.values_list('pk', 'name')


class Report(models.Model):

    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey()


class AbstractCategory(models.Model):
    name = models.CharField(unique=True, max_length=256)

    class Meta:
        abstract = True
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.name

    @classmethod
    def as_choices(cls):
        return cls.objects.values_list('pk', 'name')
