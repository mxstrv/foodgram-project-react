from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import (IsAuthenticatedOrReadOnly,
                                        IsAuthenticated)

from core.pdf_generation import generate_pdf
from recipes.models import (Tag, Recipe, Ingredient, Favorite,
                            ShoppingCart, RecipeIngredient)
from users.models import CustomUser, Subscription
from .filters import IngredientSearch, RecipeFilter
from .paginations import PageNumberLimitPagination
from .permissions import (IsAuthenticatedOrReadOnlyForProfile,
                          AuthorOrReadOnlyForRecipes)
from .serializers import (UserSerializer, TagSerializer,
                          RecipeSerializer,
                          IngredientSerializer, CreateRecipeSerializer,
                          SubscribeSerializer, FavoriteSerializer,
                          ShoppingCartSerializer)
from .utils import instance_create_connection, instance_delete_connection


class CustomUserViewSet(UserViewSet):
    """ ViewSet для пользователя."""
    queryset = CustomUser.objects.all()
    permission_classes = [IsAuthenticatedOrReadOnlyForProfile, ]
    serializer_class = UserSerializer
    pagination_class = PageNumberLimitPagination

    def get_object(self):
        """ Для GET запроса по id пользователя."""
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
                context={'request': request}
            )
            serializer.is_valid(raise_exception=True)
            Subscription.objects.create(user=user, author=subscribe_user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
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
    filter_backends = (IngredientSearch,)
    search_fields = ('^name',)


class RecipeViewSet(viewsets.ModelViewSet):
    """ ViewSet для рецептов."""
    queryset = Recipe.objects.all()
    permission_classes = [AuthorOrReadOnlyForRecipes, ]
    pagination_class = PageNumberLimitPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return RecipeSerializer
        return CreateRecipeSerializer

    @action(
        methods=['post', 'delete'],
        detail=True,
        permission_classes=[IsAuthenticated], )
    def favorite(self, request, **kwargs):
        """ Добавление/удаление рецепта в избранное."""
        favorite_recipe = get_object_or_404(Recipe,
                                            pk=self.kwargs.get('pk'))

        if request.method == 'POST':
            return instance_create_connection(request,
                                              favorite_recipe,
                                              FavoriteSerializer)
        return instance_delete_connection(
            request, Favorite, favorite_recipe)

    @action(
        methods=['post', 'delete'],
        detail=True,
        permission_classes=[IsAuthenticated]
    )
    def shopping_cart(self, request, **kwargs):
        """ Добавление рецепта в список для покупок."""
        shopping_recipe = get_object_or_404(Recipe,
                                            pk=self.kwargs.get('pk'))

        if request.method == 'POST':
            return instance_create_connection(request,
                                              shopping_recipe,
                                              ShoppingCartSerializer)
        return instance_delete_connection(
            request, ShoppingCart, shopping_recipe)

    @action(
        methods=['get'],
        detail=False,
        permission_classes=[IsAuthenticated]
    )
    def download_shopping_cart(self, request):
        """ Метод для скачивания pdf-файла с ингредиентами."""
        ingredients_list = RecipeIngredient.objects.filter(
            recipe__shopping_cart__user=request.user
        ).values('ingredient__name', 'ingredient__measurement_unit'
                 ).annotate(total_amount=Sum('amount'))
        result = generate_pdf(ingredients_list)
        response = HttpResponse(
            result,
            content_type='application/pdf')
        response[
            'Content-Disposition'] = 'attachment; filename="shopping_list.pdf"'

        return response
