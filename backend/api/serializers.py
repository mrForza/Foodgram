from django.contrib.auth.hashers import make_password
from django.http import Http404
from django.shortcuts import get_object_or_404
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from api.validators import (validate_amount, validate_field_existance,
                            validate_repetetive_values)
from recipes.models import (BaseRecipe, Ingredient, Recipe, RecipeFavourite,
                            RecipeIngredient, RecipeTag, ShoppingCart, Tag)
from users.models import CustomUser, Subscription


class CustomUserRetrieveSerializer(serializers.ModelSerializer):
    email = serializers.CharField(validators=[])
    username = serializers.CharField(validators=[])
    is_subscribed = serializers.SerializerMethodField(read_only=True)

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return obj.author.filter(
            user=request.user.id
        ).exists()

    class Meta:
        model = CustomUser
        fields = (
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'is_subscribed'
        )


class CustomUserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True
    )

    def create(self, validated_data):
        raw_password = validated_data.get('password')
        validated_data['password'] = make_password(raw_password)
        return super().create(validated_data)

    class Meta:
        model = CustomUser
        fields = (
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'password'
        )


class TokenLoginSerializer(TokenObtainPairSerializer):
    email = serializers.CharField(write_only=True)
    password = serializers.CharField(write_only=True)
    auth_token = serializers.CharField(read_only=True)

    class Meta:
        fields = (
            'email',
            'password',
            'auth_token'
        )


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = '__all__'


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = '__all__'


class RecipeIngredientSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()
    amount = serializers.IntegerField()

    class Meta:
        model = RecipeIngredient
        fields = (
            'id',
            'amount'
        )


class RecipeIngredientRetrieveSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = RecipeIngredient
        fields = (
            'id',
            'name',
            'measurement_unit',
            'amount'
        )


class RecipeRetrieveSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True)
    ingredients = serializers.SerializerMethodField()
    author = CustomUserRetrieveSerializer(many=False)
    image = Base64ImageField()
    is_favorited = serializers.SerializerMethodField(
        method_name='get_is_favorited'
    )
    is_in_shopping_cart = serializers.SerializerMethodField(
        method_name='get_is_in_shopping_cart'
    )

    def get_ingredients(self, obj):
        recipe_ingredients = RecipeIngredient.objects.filter(recipe=obj)
        ingredients_data = RecipeIngredientRetrieveSerializer(
            instance=recipe_ingredients,
            many=True
        ).data
        return ingredients_data

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return obj.favorites.filter(user=request.user.id).exists()

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return obj.shopping_cart.filter(user=request.user.id).exists()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'text',
            'cooking_time',
            'image',
            'author',
            'tags',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart'
        )


class RecipeCreateSerializer(serializers.ModelSerializer):
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True
    )
    ingredients = RecipeIngredientSerializer(
        source='recipe_ingredients',
        many=True
    )
    author = CustomUserRetrieveSerializer(read_only=True)
    image = Base64ImageField()
    is_favorited = serializers.SerializerMethodField(
        method_name='get_is_favorited'
    )
    is_in_shopping_cart = serializers.SerializerMethodField(
        method_name='get_is_in_shopping_cart'
    )

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        return (request is not None and not request.user.is_anonymous
                and obj.favorites.filter(user=request.user.id).exists())

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        return (request is not None and not request.user.is_anonymous
                and obj.shopping_cart.filter(user=request.user.id).exists())

    def validate_ingredients(self, value):
        validate_field_existance(value, 'Вы не добавили ингредиенты!')
        validate_amount(value, 'Количество продуктов не может быть меньше 1!')
        validate_repetetive_values(
            value,
            'Встречаются повторяющиеся ингредиенты!'
        )
        return value

    def validate_tags(self, value):
        validate_field_existance(value, 'Вы не добавили тэги!')
        validate_repetetive_values(value, 'Встречаются повторяющиеся тэги!')
        return value

    def validate_image(self, value: str):
        validate_field_existance(value, 'Пустое поле image!')
        return value

    def create(self, validated_data: dict):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('recipe_ingredients')
        validated_data.update({
            'author': self.context.get('request').user
        })
        recipe = Recipe.objects.create(**validated_data)

        for tag_id in tags:
            RecipeTag.objects.create(
                recipe=recipe,
                tag=tag_id
            )

        for item in ingredients:
            try:
                RecipeIngredient.objects.create(
                    recipe=recipe,
                    ingredient=get_object_or_404(
                        Ingredient, pk=item.get('id')
                    ),
                    amount=item.get('amount')
                )
            except Http404:
                raise ValidationError(
                    detail='Нет ингредиентов!',
                    code=400
                )
        return recipe

    def update(self, instance: Recipe, validated_data):
        if 'tags' in validated_data.keys():
            tags = validated_data.pop('tags')
            if tags == []:
                raise ValidationError(
                    detail='No tags in tag field!',
                    code=400
                )
            RecipeTag.objects.filter(recipe=instance).delete()
            for tag_id in tags:
                RecipeTag.objects.create(
                    recipe=instance,
                    tag=tag_id
                )
        else:
            raise ValidationError(
                detail='Нет поля \'тэги\'',
                code=400
            )

        if 'recipe_ingredients' in validated_data.keys():
            ingredients = validated_data.pop('recipe_ingredients')
            if ingredients == []:
                raise ValidationError(
                    detail='Нет ингредиентов!',
                    code=400
                )
            RecipeIngredient.objects.filter(recipe=instance).delete()
            for item in ingredients:
                try:
                    RecipeIngredient.objects.create(
                        recipe=instance,
                        ingredient=get_object_or_404(
                            Ingredient,
                            pk=item.get('id')
                        ),
                        amount=item.get('amount')
                    )
                except Http404:
                    raise ValidationError(
                        detail='Нет тегов!',
                        code=400
                    )
        else:
            raise ValidationError(
                detail='Нет поля \'Ингредиенты\'',
                code=400
            )

        instance.name = validated_data.get('name', instance.name)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get(
            'cooking_time',
            instance.cooking_time
        )
        instance.image = validated_data.get('image', instance.image)
        instance.save()

        return instance

    def to_representation(self, instance):
        return RecipeRetrieveSerializer(
            instance=instance,
            context={'request': self.context.get('request')}
        ).data

    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'text',
            'cooking_time',
            'image',
            'author',
            'tags',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart'
        )


class RecipeSubscriptionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time',
        )


class SubscriptionRetrieveSerializer(CustomUserRetrieveSerializer):
    recipes = serializers.SerializerMethodField(read_only=True)
    recipes_count = serializers.SerializerMethodField(read_only=True)

    class Meta(CustomUserRetrieveSerializer.Meta):
        fields = (
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count'
        )

    def get_recipes(self, value):
        request = self.context.get('request')
        user = self.context.get('user')
        recipes = value.recipes.all()
        if request and not user.is_anonymous:
            request = self.context.get('request')
            limit = request.query_params.get('recipes_limit')
            if limit:
                recipes = recipes[:int(limit)]
        return RecipeSubscriptionSerializer(
            instance=recipes,
            many=True,
            context={'request': request}
        ).data

    def get_recipes_count(self, value):
        return value.recipes.count()


class SubscriptionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Subscription
        fields = (
            'author',
            'user',
        )

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        return SubscriptionRetrieveSerializer(
            instance=get_object_or_404(
                CustomUser,
                pk=representation.get('author')
            ),
            context={
                'request': self.context.get('request'),
                'user': get_object_or_404(
                    CustomUser,
                    pk=representation.get('user')
                )
            }
        ).data

    def validate(self, data):
        author = data.get('author')
        user = data.get('user')
        if author == user:
            raise ValidationError(
                detail='Вы не можете подписаться на самого себя!',
                code=400
            )
        if Subscription.objects.filter(
            author=author,
            user=user
        ).exists():
            raise ValidationError(
                detail='Вы уже оформили подписку!',
                code=400
            )
        return data


class FavouriteShoppingCartSerializer(serializers.ModelSerializer):
    def validate(self, data, **kwargs):
        if not Recipe.objects.filter(pk=data.get('recipe').pk).exists():
            raise ValidationError(
                detail='Нет рецепта с таким id!',
                code=400
            )
        recipe = data.get('recipe')
        if kwargs.get('class_name').objects.filter(
            recipe=recipe,
            user=self.context.get('user')
        ).exists():
            raise ValidationError(
                detail=kwargs.get('error_message'),
                code=400
            )
        return data

    class Meta:
        model = BaseRecipe
        fields = (
            'recipe',
            'user'
        )


class FavouriteSerializer(FavouriteShoppingCartSerializer):
    def validate(self, data, **kwargs):
        return super().validate(data, **{
            'class_name': RecipeFavourite,
            'error_message': 'Вы уже добавили этот рецепт в избранное!'
        })

    class Meta(FavouriteShoppingCartSerializer.Meta):
        model = RecipeFavourite


class ShoppingCartSerializer(FavouriteShoppingCartSerializer):
    def validate(self, data, **kwargs):
        return super().validate(data, **{
            'class_name': ShoppingCart,
            'error_message': 'Вы уже добавили этот рецепт в корзину!'
        })

    class Meta(FavouriteShoppingCartSerializer.Meta):
        model = ShoppingCart
