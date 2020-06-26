from django_extensions.db import fields
from django_extensions.db.models import ActivatorModel, TimeStampedModel

from django.contrib.auth import get_user_model
from django.contrib.postgres.fields import JSONField
from django.core.exceptions import ObjectDoesNotExist
from django.core.files.base import ContentFile
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import Count, OuterRef, Subquery
from django.urls import reverse_lazy
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from core.models import City
from core.utils import get_file_path

__all__ = (
    'Category',
    'Ad',
    'AdImage',
    'FavoriteAd',
    'AdReview',
    'ContactDetail',
    'Comment',
    'SavedSearch',
)


class Category(models.Model):
    name = models.CharField(max_length=256, unique=True)

    class Meta:
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.name

    @classmethod
    def as_choices(cls):
        return cls.objects.values_list('pk', 'name')

    @classmethod
    def category_ads_count(cls):
        return cls.objects.values('pk', 'name').annotate(count=Count('ad'))


class Ad(ActivatorModel, TimeStampedModel):
    NEW_STATE = 'new'
    USED_STATE = 'used'
    STATES = (
        (NEW_STATE, _('New')),
        (USED_STATE, _('Used')),
    )

    CURRENCIES = (
        ('kwd', 'KWD'),
        ('usd', 'USD'),
    )

    SELLER_TYPES = (
        (True, _('Private')),
        (False, _('Public')),
    )

    title = models.CharField(max_length=256)
    slug = fields.AutoSlugField(populate_from='title', blank=False)
    description = models.TextField(blank=False)
    state = models.CharField(max_length=5, choices=STATES, default=NEW_STATE)
    views = models.IntegerField(default=0)
    external_url = models.URLField(null=True, unique=True)
    external_phone_number = models.CharField(null=True, max_length=20)

    is_seller_private = models.BooleanField(default=False)

    publish_date = models.DateTimeField(default=timezone.now)
    premium_until = models.DateTimeField(null=True)

    price = models.IntegerField()
    currency = models.CharField(max_length=3, choices=CURRENCIES, default='kwd')

    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)

    # categories
    category = models.ForeignKey(Category, null=True, on_delete=models.SET_NULL)
    city = models.ForeignKey(City, null=True, on_delete=models.SET_NULL)

    def __str__(self):
        return self.title

    @property
    def images(self):
        return self.adimage_set.all()

    @property
    def is_able_to_republish(self):
        return timezone.now() - self.publish_date > timezone.timedelta(days=7)

    @property
    def is_new(self):
        return self.state == self.NEW_STATE

    @property
    def is_premium(self):
        return self.premium_until and self.premium_until > timezone.now()

    @property
    def external_phone_number_clean(self):
        if self.external_phone_number:
            return self.external_phone_number.replace(' ', '').replace('+', '').replace('-', '')

    def republish(self):
        if self.is_able_to_republish:
            self.publish_date = timezone.now()
            self.save()

    def get_absolute_url(self):
        return reverse_lazy('ads:ad_detail', kwargs={'pk': self.pk, 'slug': self.slug})

    def toggle_status(self):
        self.status = int(not self.status)
        self.save()

    def get_related_object(self):
        related_names = ['carad', 'mobilead', 'realestatead']
        for rel in related_names:
            try:
                related = getattr(self, rel)
            except ObjectDoesNotExist:
                related = None

            if related:
                return related


class AdImage(models.Model):
    image = models.ImageField(upload_to=get_file_path)
    is_primary = models.BooleanField(default=False)

    ad = models.ForeignKey(Ad, on_delete=models.CASCADE)

    @classmethod
    def primary_image(cls, queryset, outer_ref='pk'):
        """
        Attaches primary image from AdImage model.
        :param outer_ref:
        :param queryset:
        :return:
        """
        image_subquery = cls.objects.filter(ad=OuterRef(outer_ref), is_primary=True).values('image')
        return queryset.annotate(primary_image=Subquery(image_subquery[:1]))

    @classmethod
    def attach_to_ad(cls, ad, images, primary=True):
        for image in images:
            ad_image = cls(is_primary=primary)
            ad_image.ad = ad
            ad_image.image.save(image.name, ContentFile(image.read()))
            primary = False

    @classmethod
    def select_images(cls, pk):
        return cls.objects.filter(ad=pk).order_by('-is_primary')


class FavoriteAd(models.Model):
    saved_at = models.DateTimeField(default=timezone.now)

    ad = models.ForeignKey(Ad, on_delete=models.CASCADE)
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)

    class Meta:
        ordering = ['-saved_at']
        unique_together = ('ad', 'user', )

    def __str__(self):
        return f'{self.ad.title} - {self.user}'

    @classmethod
    def is_favorite(cls, queryset, user, outer_ref='pk'):
        """
        Checks if ad is favorite for a given user.
        :param queryset:
        :param user:
        :param outer_ref:
        :return:
        """
        favorite_subquery = cls.objects.filter(ad=OuterRef(outer_ref), user=user).only('pk')
        return queryset.annotate(is_favorite=Subquery(favorite_subquery, output_field=models.BooleanField()))


class AdReview(models.Model):
    rating = models.IntegerField(
        default=5, validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    feedback = models.TextField(max_length=1000)

    saved_at = models.DateTimeField(default=timezone.now)

    ad = models.ForeignKey(Ad, on_delete=models.CASCADE)
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)

    class Meta:
        ordering = ['-saved_at']
        unique_together = ('ad', 'user', )


class ContactDetail(models.Model):
    email = models.EmailField()
    full_name = models.CharField(max_length=256)
    phone_number = models.CharField(max_length=16)

    is_email_confirmed = models.BooleanField(default=False)
    is_phone_number_confirmed = models.BooleanField(default=False)

    email_confirmation_token = models.CharField(max_length=64, editable=False, null=True, unique=True)
    phone_number_confirmation_code = models.CharField(max_length=64, editable=False, null=True, unique=True)

    ad = models.ForeignKey('ads.Ad', on_delete=models.CASCADE)

    @property
    def phone_number_clean(self):
        if self.phone_number:
            return self.phone_number.replace(' ', '').replace('+', '').replace('-', '')


class Comment(TimeStampedModel):

    description = models.TextField()

    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    ad = models.ForeignKey(Ad, on_delete=models.CASCADE)


class SavedSearch(TimeStampedModel):
    data = JSONField()
    last_notified = models.DateTimeField(default=timezone.now)

    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)

    @property
    def search_url(self):
        data = dict(
            q=self.data.get('q'),
            seller_type=self.data.get('seller_type'),
            city=self.data.get('city'),
            price_min=self.data.get('price_min'),
            price_max=self.data.get('price_max'),
            status=self.data.get('status'),
            category=','.join(self.data.get('categories')),
        )
        query_string = '&'.join([f'{key}={value}' for key, value in data.items()])

        return f'{reverse_lazy("ads:ads")}?{query_string}'

    @property
    def info(self):
        info = []

        q = self.data.get('q')
        if q:
            info.append(f'Keyword: {q}')

        seller_type = self.data.get('seller_type')
        if seller_type:
            info.append(f'Seller Type: {seller_type.title()}')

        categories = self.data.get('categories')
        if categories:
            info.append(f'Categories: {",".join(categories)}')

        price_min = self.data.get('price_min')
        if price_min:
            info.append(f'Min Price: {price_min}')

        price_max = self.data.get('price_max')
        if price_max:
            info.append(f'Max Price: {price_max}')

        status = self.data.get('status')
        if status:
            info.append(f'Status: {status.title()}')

        return ', '.join(info)
