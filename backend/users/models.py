from django.contrib.auth.models import AbstractUser
from django.db import models

from users.constants import (HELP_TEXT, MAX_CHARFIELD_LENGTH,
                             MAX_EMAILFIELD_LENGTH, MAX_SIZE_OF_JWT)
from users.validators import username_validator


class CustomUser(AbstractUser):
    email = models.EmailField(
        verbose_name='Электронная почта',
        help_text=HELP_TEXT.get('email'),
        max_length=MAX_EMAILFIELD_LENGTH,
        unique=True
    )
    username = models.CharField(
        verbose_name='Логин',
        help_text=HELP_TEXT.get('username'),
        max_length=MAX_CHARFIELD_LENGTH,
        unique=True,
        validators=(username_validator, )
    )
    first_name = models.CharField(
        verbose_name='Имя',
        max_length=MAX_CHARFIELD_LENGTH
    )
    last_name = models.CharField(
        verbose_name='Фамилия',
        max_length=MAX_CHARFIELD_LENGTH
    )
    password = models.CharField(
        verbose_name='Пароль',
        help_text=HELP_TEXT.get('password'),
        max_length=MAX_CHARFIELD_LENGTH
    )

    USERNAME_FIELD = 'email'

    REQUIRED_FIELDS = ('username', 'first_name', 'last_name')

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('email', )

    def __str__(self) -> str:
        return f'Пользователь {self.first_name} {self.last_name}'


class ExpiredToken(models.Model):
    value = models.CharField(
        verbose_name='Значение',
        help_text=HELP_TEXT.get('value'),
        max_length=MAX_SIZE_OF_JWT
    )

    user = models.OneToOneField(
        verbose_name='Пользователь',
        to=CustomUser,
        on_delete=models.CASCADE
    )

    class Meta:
        verbose_name = 'Истёкший токен'
        verbose_name_plural = 'Истёкшие токены'

    def __str__(self) -> str:
        return (f'Истёкший токен пользователя {self.user}\n'
                f'Значение токена: {self.value}')


class Subscription(models.Model):
    author = models.ForeignKey(
        to=CustomUser,
        on_delete=models.CASCADE,
        related_name='author',
        verbose_name='Автор рецепта'
    )

    user = models.ForeignKey(
        to=CustomUser,
        on_delete=models.CASCADE,
        related_name='subscriber',
        verbose_name='Пользователь'
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'

    def __str__(self) -> str:
        return (f'Пользователь {self.user} подписался '
                f'на автора {self.author}')
