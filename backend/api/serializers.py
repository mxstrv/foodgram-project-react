import base64

from django.core.files.base import ContentFile
from django.core.validators import RegexValidator
from rest_framework import serializers

from users.models import CustomUser
from recipes.models import Tag, Recipe, RecipeIngredient, Ingredient


class UserSerializer(serializers.ModelSerializer):
    """ Сериализатор для работы с пользователем"""
    # TODO Добавить подписку на других пользователей
    first_name = serializers.CharField(max_length=150, required=True)
    last_name = serializers.CharField(max_length=150, required=True)
    email = serializers.CharField(max_length=254, required=True)
    username = serializers.CharField(max_length=150, required=True, validators=[
        RegexValidator(
            regex=r'^[\w.@+-]+',
            message='Неподходящий формат имени пользователя')])

    class Meta:
        model = CustomUser
        fields = [
            "email",
            "id",
            "username",
            "first_name",
            "last_name",
            "password",
        ]
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        """ Создание нового пользователя."""
        user = CustomUser(
            email=validated_data['email'],
            username=validated_data['username'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
        )
        user.set_password(validated_data['password'])
        user.save()
        return user


class Base64ImageField(serializers.ImageField):
    """ Сериализатор для работы с изображениями в Base64."""

    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)


class TagSerializer(serializers.ModelSerializer):
    """ Сериализатор для тэгов."""

    class Meta:
        model = Tag
        fields = '__all__'


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = '__all__'


class RecipeIngredientSerializer(serializers.ModelSerializer):
    ingredient = IngredientSerializer()

    class Meta:
        model = RecipeIngredient
        fields = '__all__'


class RecipeSerializer(serializers.ModelSerializer):
    """ Сериализатор для рецептов."""
    image = Base64ImageField(required=True, allow_null=False)
    author = UserSerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    ingredients = RecipeIngredientSerializer(many=True, read_only=True)

    class Meta:
        model = Recipe
        fields = '__all__'

    def create(self, validated_data):
        validated_data['author'] = self.context['request'].user
        return super().create(validated_data)
