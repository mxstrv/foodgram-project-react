from django.core.validators import RegexValidator
from django.db import models


class Tag(models.Model):
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
