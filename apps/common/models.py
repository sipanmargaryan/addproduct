from django.db import models

from core.models import AbstractCategory
from core.utils import get_file_path


class Article(models.Model):
    title = models.CharField(max_length=256, unique=True)
    description = models.TextField()

    def __str__(self):
        return self.title


class Category(AbstractCategory):
    class Meta:
        verbose_name_plural = 'Service Categories'


class Service(models.Model):
    name = models.CharField(max_length=256)
    opening_time = models.TimeField()
    closing_time = models.TimeField()
    cover = models.ImageField(upload_to=get_file_path)

    address = models.CharField(max_length=512)

    category = models.ForeignKey(Category, on_delete=models.CASCADE)

    def __str__(self):
        return self.name
