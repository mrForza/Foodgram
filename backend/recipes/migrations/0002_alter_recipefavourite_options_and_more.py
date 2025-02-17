# Generated by Django 5.0.1 on 2024-01-26 12:20

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='recipefavourite',
            options={'default_related_name': 'favorites', 'verbose_name': 'Избранное', 'verbose_name_plural': 'Избранные'},
        ),
        migrations.AlterModelOptions(
            name='shoppingcart',
            options={'default_related_name': 'shopping_cart', 'verbose_name': 'Корзина', 'verbose_name_plural': 'Корзины'},
        ),
        migrations.AlterField(
            model_name='recipeingredient',
            name='amount',
            field=models.IntegerField(default=1, validators=[django.core.validators.MinValueValidator(limit_value=1, message='Количество ингредиентов не может быть меньше 1'), django.core.validators.MaxValueValidator(limit_value=100, message='Количество ингредиентов не может быть больше 100 минут')], verbose_name='Количество продуктов'),
        ),
    ]
