import json

from django.core.management.base import BaseCommand

from recipes.models import Ingredient


class Command(BaseCommand):
    """
    Данный скрипт наполняет базу данных информацией
    из файла .json.
    Файл находится в ../static/data/ingredients.json
    Запуск: python manage.py recipes_json
    """
    help = 'Загружает ингредиенты из JSON файла в базу данных'

    def handle(self, *args, **options):
        json_path = 'static/data/ingredients.json'

        with open(json_path, encoding='utf-8') as file:
            json_data = json.load(file)
            for ingredient in json_data:
                if not Ingredient.objects.filter(
                        name=ingredient['name'],
                        measurement_unit=ingredient['measurement_unit']
                ).exists():
                    Ingredient.objects.create(
                        name=ingredient['name'],
                        measurement_unit=ingredient['measurement_unit'])
