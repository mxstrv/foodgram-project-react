from django.core.validators import RegexValidator
from django.db.transaction import atomic
from rest_framework import serializers, status
from rest_framework.exceptions import ValidationError
from rest_framework.fields import SerializerMethodField

from .fields import Base64ImageField
from recipes.models import (Tag, Recipe, RecipeIngredient,
                            Ingredient, RecipeTag, Favorite, ShoppingCart)
from users.models import CustomUser, Subscription


class UserSerializer(serializers.ModelSerializer):
    """
    Сериализатор для работы с пользователем.
    """
    first_name = serializers.CharField(max_length=150, required=True)
    last_name = serializers.CharField(max_length=150, required=True)
    email = serializers.CharField(max_length=254, required=True)
    username = serializers.CharField(
        max_length=150, required=True,
        validators=[
            RegexValidator(
                regex=r'^[\w.@+-]+',
                message='Неподходящий формат имени пользователя')])
    is_subscribed = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = CustomUser
        fields = [
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'password',
            'is_subscribed',
        ]
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        """ Создание нового пользователя. """
        user = CustomUser(
            email=validated_data['email'],
            username=validated_data['username'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
        )
        user.set_password(validated_data['password'])
        user.save()
        return user

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        return Subscription.objects.filter(
            user=request.user, author=obj
        ).exists()


class SubscribeSerializer(serializers.ModelSerializer):
    """
    Сериализатор для работы с подписками/отписками.
    """
    recipes_count = SerializerMethodField()
    recipes = SerializerMethodField()
    is_subscribed = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = CustomUser
        fields = [
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count'
        ]
        read_only_fields = [
            'email',
            'username',
            'first_name',
            'last_name'
        ]

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        return Subscription.objects.filter(
            user=request.user, author=obj
        ).exists()

    def validate(self, data):
        author = self.instance
        user = self.context.get('request').user
        if Subscription.objects.filter(author=author, user=user).exists():
            raise ValidationError(
                detail='Вы уже подписаны на этого пользователя!',
                code=status.HTTP_400_BAD_REQUEST
            )
        if user == author:
            raise ValidationError(
                detail='Нельзя подписаться на себя!',
                code=status.HTTP_400_BAD_REQUEST
            )
        return data

    def get_recipes(self, obj):
        request = self.context.get('request')
        limit = request.GET.get('recipes_limit')
        recipes = obj.recipes.all()
        if limit:
            recipes = recipes[:int(limit)]
        serializer = RecipeSerializer(recipes, many=True, read_only=True)
        return serializer.data

    def get_recipes_count(self, obj):
        return obj.recipes.count()


class TagSerializer(serializers.ModelSerializer):
    """
    Сериализатор для тэгов.
    """

    class Meta:
        model = Tag
        fields = '__all__'


class IngredientSerializer(serializers.ModelSerializer):
    """
    Сериализатор для ингредиентов.
    """

    class Meta:
        model = Ingredient
        fields = [
            'id',
            'name',
            'measurement_unit',
        ]


class RecipeIngredientSerializer(serializers.ModelSerializer):
    """
    Сериализатор для ингредиентов в рецепте.
    """
    id = serializers.ReadOnlyField(
        source='ingredient.id')
    name = serializers.ReadOnlyField(
        source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit')

    class Meta:
        model = RecipeIngredient
        fields = [
            'id',
            'name',
            'amount',
            'measurement_unit',
        ]


class RecipeSerializer(serializers.ModelSerializer):
    """
    Сериализатор для работы с GET запросами рецептов
    + Response при POST,PATCH запросах.
    """
    author = UserSerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    image = Base64ImageField(required=True, allow_null=False)
    ingredients = RecipeIngredientSerializer(many=True, read_only=True)
    is_favorited = serializers.SerializerMethodField(read_only=True)
    is_in_shopping_cart = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Recipe
        fields = [
            'id',
            'author',
            'tags',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'text',
            'image',
            'cooking_time'
        ]

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        return Favorite.objects.filter(
            user=request.user, recipe=obj
        ).exists()

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        return ShoppingCart.objects.filter(
            user=request.user, recipe=obj
        ).exists()


class AddIngredientRecipeSerializer(serializers.ModelSerializer):
    """
    Сериализатор, отвечающий за добавление ингредиента в рецепт.
    """
    id = serializers.IntegerField()
    amount = serializers.IntegerField(min_value=1)

    class Meta:
        model = RecipeIngredient
        fields = [
            'id',
            'amount'
        ]


class CreateRecipeSerializer(serializers.ModelSerializer):
    """
    Сериализатор, обрабатывающий POST/PATCH запросы к рецептам.
    """
    author = UserSerializer(read_only=True)
    ingredients = AddIngredientRecipeSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True)
    image = Base64ImageField(required=True)

    class Meta:
        model = Recipe
        fields = [
            'id',
            'author',
            'tags',
            'ingredients',
            'name',
            'text',
            'image',
            'cooking_time'
        ]

    def validate(self, data):
        ingredient_list = []
        for ingredient in data.get('ingredients'):
            if ingredient.get('amount') < 1:
                raise serializers.ValidationError({
                    'amount': 'Ингредиентов должно быть больше одного!'
                })
            if ingredient.get('id') in ingredient_list:
                raise serializers.ValidationError({
                    'ingredient': 'Ингредиенты не могут повторяться!'
                })
            ingredient_list.append(ingredient.get('id'))
        return data

    def create_ingredients(self, ingredients, recipe):
        ingredient_list = []
        for ingredient in ingredients:
            ingredient_list.append(RecipeIngredient(
                recipe=recipe, ingredient=ingredient,
                amount=ingredient.get('amount')))
        RecipeIngredient.objects.bulk_create(ingredient_list)

    def create_tags(self, tags, recipe):
        tags_list = []
        for tag in tags:
            tags_list.append(RecipeTag(recipe=recipe, tag=tag))
        RecipeTag.objects.bulk_create(tags_list)

    @atomic
    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        author = self.context.get('request').user
        recipe = Recipe.objects.create(author=author, **validated_data)
        self.create_ingredients(ingredients, recipe)
        self.create_tags(tags, recipe)
        return recipe

    @atomic
    def update(self, instance, validated_data):
        RecipeIngredient.objects.filter(recipe=instance).delete()
        ingredients = validated_data.pop('ingredients')
        self.create_ingredients(ingredients, instance)
        RecipeTag.objects.filter(recipe=instance).delete()
        tags = validated_data.pop('tags')
        self.create_tags(tags, instance)
        super().update(instance, validated_data)
        return instance

    def to_representation(self, instance):
        return RecipeSerializer(instance, context={
            'request': self.context.get('request')
        }).data


class FavoriteSerializer(serializers.ModelSerializer):
    """
    Сериализатор, обрабатывающий добавление рецепта в избранное.
    """

    class Meta:
        model = Recipe
        fields = [
            'id',
            'name',
            'image',
            'cooking_time',
        ]

        read_only_fields = [
            'image',
            'name',
            'cooking_time'
        ]

    def validate(self, data):
        recipe = self.instance
        user = self.context.get('request').user
        if Favorite.objects.filter(recipe=recipe, user=user).exists():
            raise ValidationError(
                detail='Рецепт уже в избранном!',
                code=status.HTTP_400_BAD_REQUEST
            )
        return data


class ShoppingCartSerializer(serializers.ModelSerializer):
    """
    Сериализатор, обрабатывающий добавление рецепта в корзину для покупок.
    """

    class Meta:
        model = Recipe
        fields = [
            'id',
            'name',
            'image',
            'cooking_time',
        ]

        read_only_fields = [
            'image',
            'name',
            'cooking_time'
        ]

    def validate(self, data):
        recipe = self.instance
        user = self.context.get('request').user
        if ShoppingCart.objects.filter(recipe=recipe, user=user).exists():
            raise ValidationError(
                detail='Рецепт уже в списке для покупок!',
                code=status.HTTP_400_BAD_REQUEST
            )
        return data
