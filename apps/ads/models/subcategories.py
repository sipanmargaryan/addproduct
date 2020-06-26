from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone
from django.utils.text import gettext_lazy as _

__all__ = (
    'CarMakeCategory',
    'CarModelCategory',
    'CarAd',
    'MobileBrandCategory',
    'MobileModelCategory',
    'MobileAd',
    'RealEstateAd',
)


class BaseCategory(models.Model):
    name = models.CharField(max_length=256, unique=True)

    class Meta:
        abstract = True

    def __str__(self):
        return self.name

    @classmethod
    def as_choices(cls):
        return cls.objects.values_list('pk', 'name')


class BaseAd(models.Model):
    ad = models.OneToOneField('ads.Ad', on_delete=models.CASCADE)

    class Meta:
        abstract = True


class CarMakeCategory(BaseCategory):
    class Meta:
        verbose_name_plural = 'Car Makes'


class CarModelCategory(models.Model):
    name = models.CharField(max_length=256)
    make = models.ForeignKey(CarMakeCategory, on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = 'Car Models'
        unique_together = (('name', 'make', ), )

    def __str__(self):
        return self.name

    @classmethod
    def as_choices(cls):
        return cls.objects.values_list('pk', 'name')


class CarAd(BaseAd):
    YEAR_VALIDATORS = (
        MinValueValidator(1900),
        MaxValueValidator(timezone.now().year),
    )
    BODY_STYLES = (
        ('sedan', _('Sedan')),
        ('hatchback', _('Hatchback')),
        ('wagon', _('Wagon')),
        ('coupe', _('Coupe')),
        ('convertible', _('Convertible')),
        ('suv/truck', _('SUV/Truck')),
        ('pickup truck', _('Pickup Truck')),
        ('minivan/minibus', _('Minivan/Minibus')),
        ('van', _('Van')),
        ('limousine', _('Limousine')),
    )

    make = models.ForeignKey(CarMakeCategory, null=True, on_delete=models.SET_NULL)
    model = models.ForeignKey(CarModelCategory, null=True, on_delete=models.SET_NULL)

    mileage = models.IntegerField(null=True)
    year = models.IntegerField(validators=YEAR_VALIDATORS, null=True)
    body_style = models.CharField(default=None, null=True, max_length=16, choices=BODY_STYLES)


class MobileBrandCategory(BaseCategory):
    class Meta:
        verbose_name_plural = 'Mobile Brands'


class MobileModelCategory(models.Model):
    name = models.CharField(max_length=256)
    brand = models.ForeignKey(MobileBrandCategory, on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = 'Mobile Models'
        unique_together = (('name', 'brand', ), )

    def __str__(self):
        return self.name

    @classmethod
    def as_choices(cls):
        return cls.objects.values_list('pk', 'name')


class MobileAd(BaseAd):
    brand = models.ForeignKey(MobileBrandCategory, null=True, on_delete=models.SET_NULL)
    model = models.ForeignKey(MobileModelCategory, null=True, on_delete=models.SET_NULL)


class RealEstateAd(BaseAd):
    FOR_SELL = 'for_sell'
    FOR_RENT = 'for_rent'
    CHOICES = (
        (FOR_SELL, 'FOR SELL'),
        (FOR_RENT, 'FOR RENT'),
    )
    ESTATE_TYPES = (
        ('shop', _('Shop')),
        ('apartment', _('Apartment')),
        ('villa', _('Villa')),
    )

    purpose = models.CharField(max_length=16, default=FOR_SELL, choices=CHOICES)
    bedrooms = models.IntegerField(null=True, default=1)
    bathrooms = models.IntegerField(null=True, default=1)
    estate_type = models.CharField(default=None, null=True, max_length=16, choices=ESTATE_TYPES)
