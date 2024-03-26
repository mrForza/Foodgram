from django_filters.rest_framework import (BooleanFilter, CharFilter,
                                           FilterSet,
                                           ModelMultipleChoiceFilter)
from rest_framework.filters import SearchFilter

from recipes.models import Recipe, Tag


class IngredientFilter(SearchFilter):
    search_param = 'name'


class RecipeFilter(FilterSet):
    author = CharFilter()
    tags = ModelMultipleChoiceFilter(
        field_name='tags__slug',
        queryset=Tag.objects.all(),
        label='Tags',
        to_field_name='slug'
    )
    is_favorited = BooleanFilter(method='get_is_favorite')
    is_in_shopping_cart = BooleanFilter(method='get_is_in_shopping_cart')

    def get_is_favorite(self, queryset, name, value):
        return (queryset.filter(favorites__user=self.request.user.id)
                if value else queryset)

    def get_is_in_shopping_cart(self, queryset, name, value):
        return (queryset.filter(shopping_cart__user=self.request.user.id)
                if value else queryset)

    class Meta:
        model = Recipe
        fields = (
            'author',
            'tags'
        )
