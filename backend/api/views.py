from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from djoser.views import UserViewSet

from recipes.models import Tag, Recipe, Ingredient
from users.models import CustomUser
from .permissions import IsAuthenticatedOrReadOnlyForProfile, AuthorOrReadOnlyForRecipes
from .serializers import UserSerializer, TagSerializer, RecipeSerializer, IngredientSerializer


# TODO Там, где надо, добавить поиск во вьюсеты

class CustomUserViewSet(UserViewSet):
    """ ViewSet для пользователя."""
    queryset = CustomUser.objects.all()
    permission_classes = [IsAuthenticatedOrReadOnlyForProfile, ]
    serializer_class = UserSerializer
    pagination_class = PageNumberPagination

    def get_object(self):
        # Для GET запроса по id пользователя
        return get_object_or_404(CustomUser,
                                 id=self.kwargs.get('id'))


class TagViewSet(viewsets.ModelViewSet):
    """ ViewSet для тэгов."""
    queryset = Tag.objects.all()
    permission_classes = [IsAuthenticatedOrReadOnly, ]
    http_method_names = ['get']
    serializer_class = TagSerializer
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    """ ViewSet для рецептов."""
    queryset = Recipe.objects.all()
    permission_classes = [AuthorOrReadOnlyForRecipes, ]
    serializer_class = RecipeSerializer
    pagination_class = PageNumberPagination


class IngredientViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    permission_classes = [IsAuthenticatedOrReadOnly, ]
    http_method_names = ['get']
    serializer_class = IngredientSerializer
    pagination_class = PageNumberPagination