import json
import os

from django.conf import settings
from django.core.management.base import BaseCommand

from ads.models import CarMakeCategory, CarModelCategory


class Command(BaseCommand):
    help = 'Initialize car data'

    def handle(self, *args, **options):
        with open(os.path.join(settings.BASE_DIR, 'json_data/car_brands_models.json'), 'rb') as f:
            models = json.loads(f.read())

        for model in models:
            make, _ = CarMakeCategory.objects.get_or_create(name=model['brand'])
            CarModelCategory.objects.get_or_create(name=model['model'], make=make)

            self.stdout.write(self.style.SUCCESS(f'Successfully imported {model["brand"]} - {model["model"]}'))
