from django.contrib import admin

from recipes.models import (Ingredient, Recipe, RecipeFavourite, ShoppingCart,
                            Tag)

EMPTY_MESSAGE = 'Незаполненное поле'


class IngredientsInLine(admin.TabularInline):
    model = Recipe.ingredients.through


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'color',
        'slug'
    )
    search_fields = ('name', )
    empty_value_display = EMPTY_MESSAGE


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'measurement_unit'
    )
    search_fields = ('name', )
    empty_value_display = EMPTY_MESSAGE


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'author',
        'count_favorites'
    )
    list_filter = ('tags', )
    search_fields = (
        'name',
        'author__username'
    )
    inlines = (IngredientsInLine, )
    empty_value_display = EMPTY_MESSAGE

    def count_favorites(self, obj):
        return obj.favorites.count()


@admin.register(RecipeFavourite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'user',
        'recipe'
    )
    search_fields = (
        'user__username',
        'user__email'
    )
    empty_value_display = EMPTY_MESSAGE


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'user',
        'recipe'
    )
    search_fields = (
        'user__username',
        'user__email'
    )
    empty_value_display = EMPTY_MESSAGE
