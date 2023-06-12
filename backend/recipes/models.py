from django.core.validators import RegexValidator, MinValueValidator
from django.db import models

from users.models import CustomUser


class Tag(models.Model):
    """ Модель тэгов для рецептов."""
    name = models.CharField(
        'Название тэга',
        max_length=200,
        blank=False,
        unique=True,
    )
    color = models.CharField(
        'Цвет тэга',
        max_length=7,
        unique=False,
        blank=True,
        validators=[RegexValidator(
            regex=r"^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$",
            message='Неподходящее название'), ]
    )
    slug = models.SlugField(
        max_length=200,
        unique=True,
        validators=[RegexValidator(
            regex=r'^[-a-zA-Z0-9_]+$',
            message='Неподходящее название'), ]
    )


class Ingredient(models.Model):
    """ Модель для хранения ингредиентов для рецептов. """
    name = models.CharField(
        'Название ингредиента',
        max_length=150  # TODO CHECK MAX LENGTH
    )
    measurement_unit = models.CharField('Единица измерения ингредиента',
                                        max_length=10)


class Recipe(models.Model):
    """ Модель для рецептов."""
    name = models.CharField('Название блюда',
                            max_length=200,
                            blank=False, )
    text = models.CharField('Описание блюда',
                            max_length=10000,  # TODO CHECK SIZE
                            blank=False)
    cooking_time = models.IntegerField('Время приготовления блюда',
                                       blank=False,
                                       validators=[MinValueValidator(1), ])

    image = models.ImageField(
        upload_to='recipes/images/',
        blank=False,
        null=False,
    )
    author = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='Автор рецепта'
    )
    tags = models.ManyToManyField(
        Tag,
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredient'
    )


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
    )
    amount = models.IntegerField(
        validators=[
            MinValueValidator(1, message='not less than 1')]
    )
