from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from djoser.views import UserViewSet

from recipes.models import Tag, Recipe, Ingredient
from users.models import CustomUser
from .permissions import IsAuthenticatedOrReadOnlyForProfile, AuthorOrReadOnlyForRecipes
from .serializers import (UserSerializer, TagSerializer,
                          RecipeSerializer,
                          IngredientSerializer, CreateRecipeSerializer)


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


class IngredientViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    permission_classes = [IsAuthenticatedOrReadOnly, ]
    http_method_names = ['get']
    serializer_class = IngredientSerializer
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    """ ViewSet для рецептов."""
    queryset = Recipe.objects.all()
    permission_classes = [AuthorOrReadOnlyForRecipes, ]
    pagination_class = PageNumberPagination

    # def perform_create(self, serializer):
    #     serializer.save(author=self.request.user)

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return RecipeSerializer
        return CreateRecipeSerializer

    # TODO WTF?
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({'request': self.request})
        return context
