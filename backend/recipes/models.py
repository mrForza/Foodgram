from colorfield.fields import ColorField
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from recipes.constants import (HELP_TEXT, MAX_AMOUNT_ERROR,
                               MAX_AMOUNT_OF_PRODUCTS, MAX_CHARFIELD_LENGTH,
                               MAX_COLORFIELD_LENGTH, MAX_COOKING_TIME,
                               MAX_COOKING_TIME_ERROR, MAX_TEXTFIELD_LENGTH,
                               MIN_AMOUNT_ERROR, MIN_AMOUNT_OF_PRODUCTS,
                               MIN_COOKING_TIME, MIN_COOKING_TIME_ERROR)
from users.models import CustomUser


class Tag(models.Model):
    name = models.CharField(
        verbose_name='Название',
        max_length=MAX_CHARFIELD_LENGTH
    )

    color = ColorField(
        verbose_name='Цвет',
        help_text=HELP_TEXT.get('tag_color'),
        max_length=MAX_COLORFIELD_LENGTH
    )

    slug = models.SlugField(
        verbose_name='Слаг',
        help_text=HELP_TEXT.get('tag_slug'),
        max_length=MAX_CHARFIELD_LENGTH
    )

    class Meta:
        ordering = ('name', )
        verbose_name = 'Тэг',
        verbose_name_plural = 'Тэги'

    def __str__(self) -> str:
        return f'Тэг: {self.slug}'


class Ingredient(models.Model):
    name = models.CharField(
        verbose_name='Название',
        max_length=MAX_CHARFIELD_LENGTH
    )

    measurement_unit = models.CharField(
        verbose_name='Единица измерения',
        help_text=HELP_TEXT.get('measurement_unit'),
        max_length=MAX_CHARFIELD_LENGTH
    )

    class Meta:
        ordering = ('name', )
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        constraints = (
            models.UniqueConstraint(
                fields=('name', 'measurement_unit'),
                name='unique_name_measurunit'
            ),
        )

    def __str__(self) -> str:
        return f'Ингредиент: {self.name} ({self.measurement_unit})'


class Recipe(models.Model):
    name = models.CharField(
        verbose_name='Название',
        max_length=MAX_CHARFIELD_LENGTH
    )

    text = models.TextField(
        verbose_name='Описание',
        max_length=MAX_TEXTFIELD_LENGTH
    )

    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления',
        validators=[
            MinValueValidator(
                limit_value=MIN_COOKING_TIME,
                message=MIN_COOKING_TIME_ERROR
            ),
            MaxValueValidator(
                limit_value=MAX_COOKING_TIME,
                message=MAX_COOKING_TIME_ERROR
            )
        ]
    )

    image = models.ImageField(
        verbose_name='Изображение',
        upload_to='media/recipes/',
        blank=False,
        null=True
    )

    author = models.ForeignKey(
        verbose_name='Автор',
        to=CustomUser,
        on_delete=models.CASCADE,
        related_name='recipes'
    )

    tags = models.ManyToManyField(
        verbose_name='Тэги',
        to=Tag,
        through='RecipeTag',
        related_name='recipes'
    )

    ingredients = models.ManyToManyField(
        verbose_name='Ингредиенты',
        to=Ingredient,
        through='RecipeIngredient',
        related_name='recipes'
    )

    class Meta:
        ordering = ('name', )
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self) -> str:
        return f'Рецепт {self.name} автора {self.author}'


class RecipeTag(models.Model):
    recipe = models.ForeignKey(
        verbose_name='Рецепты',
        to=Recipe,
        on_delete=models.CASCADE,
        related_name='recipe_tags',
    )

    tag = models.ForeignKey(
        verbose_name='Тэги',
        to=Tag,
        on_delete=models.CASCADE
    )

    class Meta:
        ordering = ('recipe', )
        verbose_name = 'Тэг рецепта'
        verbose_name_plural = 'Тэги рецептов'

    def __str__(self) -> str:
        return f'Тэг {self.tag} рецепта {self.recipe}'


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        verbose_name='Рецепты',
        to=Recipe,
        on_delete=models.CASCADE,
        related_name='recipe_ingredients',
    )

    ingredient = models.ForeignKey(
        verbose_name='Ингредиенты',
        to=Ingredient,
        on_delete=models.CASCADE,
    )

    amount = models.IntegerField(
        verbose_name='Количество продуктов',
        validators=[
            MinValueValidator(
                limit_value=MIN_AMOUNT_OF_PRODUCTS,
                message=MIN_AMOUNT_ERROR
            ),
            MaxValueValidator(
                limit_value=MAX_AMOUNT_OF_PRODUCTS,
                message=MAX_AMOUNT_ERROR
            )
        ],
        default=1
    )

    class Meta:
        ordering = ('recipe', )
        verbose_name = 'Ингредиент рецепта'
        verbose_name_plural = 'Ингредиенты рецептов'

    def __str__(self) -> str:
        return (f'Ингредиент {self.ingredient} '
                f'рецепта {self.recipe}')


class BaseRecipe(models.Model):
    user = models.ForeignKey(
        to=CustomUser,
        on_delete=models.CASCADE,
        verbose_name='Пользователь'
    )

    recipe = models.ForeignKey(
        to=Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт'
    )

    class Meta:
        ordering = ('recipe', )
        abstract = True


class RecipeFavourite(BaseRecipe):

    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранные'
        default_related_name = 'favorites'

    def __str__(self) -> str:
        return (f'Избранный рецепт {self.recipe}'
                f'пользователя {self.user}')


class ShoppingCart(BaseRecipe):

    class Meta:
        verbose_name = 'Корзина'
        verbose_name_plural = 'Корзины'
        default_related_name = 'shopping_cart'

    def __str__(self) -> str:
        return (f'Рецепт {self.recipe} продуктовой корзины'
                f'пользователя {self.user}')
