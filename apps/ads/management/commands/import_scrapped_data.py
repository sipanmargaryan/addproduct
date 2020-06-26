import functools
import json
import os

from django.conf import settings
from django.core.management.base import BaseCommand

from ads.models import (
    Ad, AdImage, CarAd, CarMakeCategory, CarModelCategory, Category, MobileAd,
    MobileBrandCategory, MobileModelCategory, RealEstateAd
)
from core.models import City
from core.utils import get_image_from_url
from users.models import User


class Command(BaseCommand):
    help = 'Initialize scrapped data'

    def handle(self, *args, **options):

        mobile_brands = MobileBrandCategory.objects.all()
        mobile_models = MobileModelCategory.objects.all()

        cities = City.objects.all()
        kuwait = City.objects.filter(name__icontains='kuwait').first()

        car_makes = CarMakeCategory.objects.all()
        car_models = CarModelCategory.objects.all()

        Ad.objects.exclude(external_url__isnull=True).delete()

        user, _ = User.objects.get_or_create(email='scrapper@masaha.app')

        with open(os.path.join(settings.BASE_DIR, 'json_data/scrapped.json'), 'rb') as f:
            items = json.loads(f.read())

        for item in items:
            if Ad.objects.filter(external_url=item.get('external_url')).exists():
                continue
            ad = Ad()
            ad.category = self.extract_category(item.get('category'))
            ad.title = item.get('title')
            ad.description = item.get('description')
            try:
                ad.price = int(item.get('price', 0))
            except ValueError:
                ad.price = 0
            ad.state = Ad.USED_STATE if item.get('used') else Ad.NEW_STATE
            ad.external_url = item.get('external_url')
            ad.external_phone_number = item.get('phone_number')
            ad.user = user

            for city in cities:
                if city.name.lower() in item.get('raw_description').lower():
                    ad.city = city
                    break

            if ad.city is None:
                ad.city = kuwait

            file = get_image_from_url(item.get('primary_image_url'))
            if file:
                try:
                    ad.save()
                except RuntimeError:
                    continue
                ad_image = AdImage(is_primary=True)
                ad_image.ad = ad

                filename = item.get('primary_image_url').split('/')[-1]
                if not any(filter(lambda ext: ext in filename, ['.jpeg', '.jpg', '.png'])):
                    filename = 'avatar.jpeg'

                ad_image.image.save(filename, file, save=True)

                if item.get('category').lower() == 'cars':
                    ad_make = None
                    ad_model = None
                    for make in car_makes:
                        if make.name.lower() in item.get('raw_description').lower():
                            ad_make = make
                            break
                    for model in car_models:
                        if model.name.lower() in item.get('raw_description').lower():
                            ad_model = model
                            break

                    if ad_make and ad_model:
                        CarAd.objects.create(ad=ad, make=ad_make, model=ad_model)
                elif item.get('category').lower() == 'mobile':
                    ad_brand = None
                    ad_model = None
                    for brand in mobile_brands:
                        if brand.name.lower() in item.get('raw_description').lower():
                            ad_brand = brand
                            break
                    for model in mobile_models:
                        if model.name.lower() in item.get('raw_description').lower():
                            ad_model = model
                            break

                    if ad_brand and ad_model:
                        MobileAd.objects.create(ad=ad, brand=ad_brand, model=ad_model)
                elif item.get('category').lower() == 'real estate':
                    estate_type = None
                    purpose = RealEstateAd.FOR_SELL
                    for e_type in RealEstateAd.ESTATE_TYPES:
                        if e_type[0] in item.get('raw_description').lower():
                            estate_type = e_type[0]
                            break
                    if 'rent' in item.get('raw_description').lower():
                        purpose = RealEstateAd.FOR_RENT

                    RealEstateAd.objects.create(ad=ad, purpose=purpose, estate_type=estate_type)

                self.stdout.write(self.style.SUCCESS(f'Successfully imported {item["title"]}'))

    @functools.lru_cache(maxsize=100)
    def extract_category(self, category_text):
        obj, _ = Category.objects.get_or_create(name__iexact=category_text, defaults={'name': category_text})

        return obj
