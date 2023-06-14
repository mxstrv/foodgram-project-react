from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import (IsAuthenticatedOrReadOnly,
                                        IsAuthenticated)

from recipes.models import Tag, Recipe, Ingredient
from users.models import CustomUser, Subscription
from .permissions import (IsAuthenticatedOrReadOnlyForProfile,
                          AuthorOrReadOnlyForRecipes)
from .serializers import (UserSerializer, TagSerializer,
                          RecipeSerializer,
                          IngredientSerializer, CreateRecipeSerializer,
                          SubscribeSerializer)


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

    @action(
        methods=['post', 'delete', ],
        detail=True,
        permission_classes=[IsAuthenticated])
    def subscribe(self, request, **kwargs):
        """ Подписка/отписка на пользователя. """
        user = request.user
        subscribe_user = get_object_or_404(
            CustomUser, id=self.kwargs.get('id'))

        if request.method == 'POST':
            serializer = SubscribeSerializer(
                subscribe_user,
                data=request.data,
                context={"request": request}
            )
            serializer.is_valid(raise_exception=True)
            Subscription.objects.create(user=user, author=subscribe_user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if request.method == 'DELETE':
            subscription = get_object_or_404(
                Subscription,
                user=user,
                author=subscribe_user)
            subscription.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False,
            permission_classes=[IsAuthenticated])
    def subscriptions(self, request):
        """ Получение списка подписок пользователя. """
        user = request.user
        queryset = CustomUser.objects.filter(following__user=user)
        pagination = self.paginate_queryset(queryset)
        serializer = SubscribeSerializer(pagination,
                                         many=True,
                                         context={'request': request})
        return self.get_paginated_response(serializer.data)


class TagViewSet(viewsets.ModelViewSet):
    """ ViewSet для тэгов."""
    queryset = Tag.objects.all()
    permission_classes = [IsAuthenticatedOrReadOnly, ]
    http_method_names = ['get']
    serializer_class = TagSerializer
    pagination_class = None


class IngredientViewSet(viewsets.ModelViewSet):
    """ ViewSet для ингредиентов."""
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
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return RecipeSerializer
        return CreateRecipeSerializer
