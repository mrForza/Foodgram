from typing import Union

from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import (GenericViewSet, ModelViewSet,
                                     ReadOnlyModelViewSet, mixins)

from api.filters import IngredientFilter, RecipeFilter
from api.pagination import CustomPagination
from api.permissions import IsAuthroOrAuthenticatedOrReadOnly
from api.serializers import (CustomUserCreateSerializer,
                             CustomUserRetrieveSerializer, FavouriteSerializer,
                             IngredientSerializer, RecipeCreateSerializer,
                             RecipeRetrieveSerializer,
                             RecipeSubscriptionSerializer,
                             ShoppingCartSerializer, SubscriptionSerializer,
                             TagSerializer)
from recipes.models import (Ingredient, Recipe, RecipeFavourite,
                            RecipeIngredient, ShoppingCart, Tag)
from users.models import CustomUser, Subscription


class RetrieveCreateMixin(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin
):
    pass


class UserViewSet(GenericViewSet, RetrieveCreateMixin):
    queryset = CustomUser.objects.all()
    permission_classes = (AllowAny, )
    http_method_names = ('get', 'post', 'delete')

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return CustomUserRetrieveSerializer
        return CustomUserCreateSerializer

    @action(
        methods=('get', ),
        detail=False,
        permission_classes=(IsAuthenticated, ),
    )
    def subscriptions(self, request):
        queryset = Subscription.objects.filter(user=request.user)
        page = self.paginate_queryset(queryset)
        serializer = SubscriptionSerializer(
            page, many=True, context={'request': request}
        )
        return self.get_paginated_response(serializer.data)

    @action(
        methods=('post', ),
        detail=True,
        permission_classes=(IsAuthenticated, )
    )
    def subscribe(self, request, pk: int):
        try:
            author = get_object_or_404(CustomUser, pk=pk)
            serializer = SubscriptionSerializer(
                data={
                    'author': author.pk,
                    'user': request.user.pk
                },
                context={'request': request}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(
                data=serializer.data,
                status=status.HTTP_201_CREATED
            )
        except ValidationError as error:
            return Response(
                data=error.detail,
                status=status.HTTP_400_BAD_REQUEST
            )

    @subscribe.mapping.delete
    def delete(self, request, pk: int):
        author = get_object_or_404(CustomUser, pk=pk)
        try:
            subscription = get_object_or_404(
                Subscription,
                author=author,
                user=request.user
            )
            subscription.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception:
            return Response(
                data='Вы не подписаны на этого пользователя!',
                status=status.HTTP_400_BAD_REQUEST
            )


class TagViewSet(ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AllowAny, )
    pagination_class = None


class IngredientViewSet(ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (AllowAny, )
    pagination_class = None
    filter_backends = (IngredientFilter, )
    search_fields = ('^name', )


class RecipeViewSet(ModelViewSet):
    queryset = Recipe.objects.all()
    permission_classes = (IsAuthroOrAuthenticatedOrReadOnly, )
    filter_backends = (DjangoFilterBackend, )
    filterset_class = RecipeFilter
    pagination_class = CustomPagination
    http_method_names = ('get', 'post', 'patch', 'delete')

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return RecipeRetrieveSerializer
        return RecipeCreateSerializer

    @action(
        methods=('get', ),
        detail=False,
        permission_classes=(IsAuthenticated, )
    )
    def download_shopping_cart(self, request):
        file_name = 'shopping_list'
        shopping_list = 'Продуктовая корзина:'

        ingredients = RecipeIngredient.objects.filter(
            recipe__shopping_cart__user=request.user
        ).values(
            'ingredient__name',
            'ingredient__measurement_unit'
        ).annotate(amount=Sum('amount'))

        for index, ingredient in enumerate(ingredients):
            shopping_list += (
                f'\n{ingredient.get("ingredient__name")}; '
                f'{ingredient.get("amount")}; '
                f'{ingredient.get("ingredient__measurement_unit")}\n'
            )
            if index < ingredients.count() - 1:
                shopping_list += '; '

        response = HttpResponse(
            shopping_list, 'Content-Type: application/pdf'
        )
        response['Content-Disposition'] = (
            f'attachment; filename="{file_name}.pdf"'
        )
        return response

    @action(
        methods=('post', ),
        detail=True,
    )
    def shopping_cart(self, request, pk: int):
        return create_instance(
            serializer_class=ShoppingCartSerializer,
            user=request.user,
            pk=pk
        )

    @shopping_cart.mapping.delete
    def delete_shopping_cart(self, request, pk):
        return delete_instance(
            class_name=ShoppingCart,
            user=request.user,
            pk=pk,
            error_message=('Вы не добавили этот рецепт в корзину! '
                           'Либо такого рецепта не существует!')
        )

    @action(
        methods=('post', ),
        detail=True,
        permission_classes=(IsAuthenticated, )
    )
    def favorite(self, request, pk: int):
        return create_instance(
            serializer_class=FavouriteSerializer,
            user=request.user,
            pk=pk
        )

    @favorite.mapping.delete
    def delete_favourite(self, request, pk: int):
        return delete_instance(
            class_name=RecipeFavourite,
            user=request.user,
            pk=pk,
            error_message=('Вы не добавили этот рецепт в избранное! '
                           'Либо такого рецепта не существует!')
        )


def create_instance(
    serializer_class: Union[FavouriteSerializer, ShoppingCartSerializer],
    user: CustomUser, pk: int
):
    try:
        serializer = serializer_class(
            data={'user': user.pk, 'recipe': pk},
            context={'user': user}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            data=RecipeSubscriptionSerializer(
                instance=serializer.validated_data.get('recipe')
            ).data,
            status=status.HTTP_201_CREATED
        )
    except ValidationError as error:
        return Response(
            data=error.detail,
            status=status.HTTP_400_BAD_REQUEST
        )


def delete_instance(
    class_name: Union[RecipeFavourite, ShoppingCart],
    user: CustomUser, pk: int, error_message
):
    recipe = get_object_or_404(Recipe, pk=pk)
    try:
        queryset = get_object_or_404(
            class_name,
            user=user,
            recipe=recipe
        )
        queryset.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    except Exception:
        return Response(
            data=error_message,
            status=status.HTTP_400_BAD_REQUEST
        )
