import csv

from django.conf import settings
from django.core.management import BaseCommand

from recipe.models import Ingredient

TABLES_DICT = {
    Ingredient: 'ingredients.csv'
}


class Command(BaseCommand):
    help = 'Load data from csv'

    def handle(self, *args, **kwargs):
        for model, base in TABLES_DICT.items():
            with open(
                f'{settings.BASE_DIR}/{base}',
                'r', encoding='utf-8'
            ) as csv_file:
                reader = csv.DictReader(
                    csv_file, fieldnames=(
                        'name',
                        'measurement_unit'
                    )
                )
                model.objects.bulk_create(model(**data) for data in reader)
        self.stdout.write(self.style.SUCCESS('Successfully load data'))
