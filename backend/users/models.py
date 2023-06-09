from django.db import models
from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):
    username = models.CharField(
        'Имя пользователя',
        max_length=150,
        blank=False,
        unique=True,
    )

    email = models.EmailField(
        'Электронная почта',
        max_length=254,
        unique=True,
        blank=False,
    )

    first_name = models.CharField(
        'Имя пользователя',
        blank=True,
        max_length=150,
    )

    last_name = models.CharField(
        'Фамилия пользователя',
        blank=True,
        max_length=150,
    )

    # TODO IS SUBSCRIBED??

    class Meta:
        ordering = ('id',)
        verbose_name = 'пользователь'
        verbose_name_plural = 'пользователи'


class Subscription(models.Model):
    # TODO IMPLEMENT
    # follower
    # following
    pass
