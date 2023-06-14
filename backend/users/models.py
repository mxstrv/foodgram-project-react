from django.db import models
from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):
    """ Кастомная модель пользователя Foodgram. """
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
        blank=False,
        null=False,
        max_length=150,
    )

    last_name = models.CharField(
        'Фамилия пользователя',
        blank=False,
        null=False,
        max_length=150,
    )

    class Meta:
        ordering = ('id',)
        verbose_name = 'пользователь'
        verbose_name_plural = 'пользователи'

    def __str__(self):
        return f'{self.username} - {self.email}'


class Subscription(models.Model):
    """ Модель подписок на пользователей. """
    user = models.ForeignKey(
        CustomUser,
        related_name='follower',
        on_delete=models.CASCADE
    )

    author = models.ForeignKey(
        CustomUser,
        related_name='following',
        on_delete=models.CASCADE
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'],
                name='follower_following_unique'
            )
        ]
        verbose_name = 'подписка'
        verbose_name_plural = 'подписки'

    def __str__(self):
        return f'{self.user} подписан на {self.author}'
