from django_extensions.db import fields

from django.db import models
from django.urls import reverse
from django.utils import timezone

import core.models
from core.utils import get_file_path


class Category(core.models.AbstractCategory):
    class Meta:
        verbose_name_plural = 'Event Categories'


class Event(models.Model):

    title = models.CharField(max_length=256, unique=True)
    slug = fields.AutoSlugField(populate_from='title', blank=False)
    address = models.CharField(max_length=256)
    description = models.TextField()
    image = models.ImageField(upload_to=get_file_path)
    price = models.CharField(max_length=256)
    registration_url = models.URLField(max_length=300)
    latitude = models.DecimalField(max_digits=50, decimal_places=45)
    longitude = models.DecimalField(max_digits=50, decimal_places=45)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()

    category = models.ForeignKey(Category, related_name='category', on_delete=models.CASCADE)
    city = models.ForeignKey(core.models.City, on_delete=models.CASCADE)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('events:event_detail', kwargs={'pk': self.pk, 'slug': self.slug})

    @classmethod
    def top_events(cls):
        return (
            cls.objects.filter(start_date__gte=timezone.now())
            .order_by('start_date')[:10]
        )
