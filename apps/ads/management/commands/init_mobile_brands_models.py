import json
import os

from django.conf import settings
from django.core.management.base import BaseCommand

from ads.models import MobileBrandCategory, MobileModelCategory


class Command(BaseCommand):
    help = 'Initialize car data'

    def handle(self, *args, **options):
        with open(os.path.join(settings.BASE_DIR, 'json_data/mobile_brands_models.json'), 'rb') as f:
            models = json.loads(f.read())

        for model in models:
            brand, _ = MobileBrandCategory.objects.get_or_create(name=model['brand'])
            MobileModelCategory.objects.get_or_create(name=model['model'], brand=brand)

            self.stdout.write(self.style.SUCCESS(f'Successfully imported {model["brand"]} - {model["model"]}'))
