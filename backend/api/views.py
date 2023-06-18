from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from fpdf import FPDF
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import (IsAuthenticatedOrReadOnly,
                                        IsAuthenticated)

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


class CustomUserViewSet(UserViewSet):
    """ ViewSet для пользователя."""
    queryset = CustomUser.objects.all()
    permission_classes = [IsAuthenticatedOrReadOnlyForProfile, ]
    serializer_class = UserSerializer
    pagination_class = PageNumberLimitPagination

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
                context={'request': request}
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
    # Необязательный параметр, но лучше указать явно
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
        """ Добавление/удаление рецепта в избранное. """
        user = request.user
        favorite_recipe = get_object_or_404(Recipe,
                                            pk=self.kwargs.get('pk'))

        if request.method == 'POST':
            serializer = FavoriteSerializer(
                favorite_recipe,
                data=request.data,
                context={'request': request},
            )
            serializer.is_valid(raise_exception=True)
            Favorite.objects.create(
                user=user, recipe=favorite_recipe)
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED)

        if request.method == 'DELETE':
            recipe = get_object_or_404(
                Favorite,
                user=user,
                recipe=favorite_recipe)
            recipe.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        methods=['post', 'delete'],
        detail=True,
        permission_classes=[IsAuthenticated]
    )
    def shopping_cart(self, request, **kwargs):
        user = request.user
        shopping_recipe = get_object_or_404(Recipe,
                                            pk=self.kwargs.get('pk'))

        if request.method == 'POST':
            serializer = ShoppingCartSerializer(
                shopping_recipe,
                data=request.data,
                context={'request': request},
            )
            serializer.is_valid(raise_exception=True)
            ShoppingCart.objects.create(
                user=user, recipe=shopping_recipe)
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED)

        if request.method == 'DELETE':
            recipe = get_object_or_404(
                ShoppingCart,
                user=user,
                recipe=shopping_recipe)
            recipe.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        methods=['get'],
        detail=False,
        permission_classes=[IsAuthenticated]
    )
    def download_shopping_cart(self, request):
        ingredients_list = RecipeIngredient.objects.filter(
            recipe__shopping_cart__user=request.user
        ).values('ingredient__name', 'ingredient__measurement_unit'
                 ).annotate(amount=Sum('amount'))
        pdf = FPDF(orientation='P', unit='mm', format='A4')
        pdf.add_page()
        pdf.add_font(
            'DejaVu', '',
            'static/fonts/DejaVuSansCondensed.ttf',
            uni=True
        )
        pdf.set_font('DejaVu', '', 16)
        pdf.cell(200, 10, txt='Ваш список покупок:', ln=1, align="C")
        for ingredient in ingredients_list:
            pdf.cell(w=0, h=10, ln=1,
                     txt=(f'{ingredient["ingredient__name"]}'
                          f' - {str(ingredient["amount"])}'
                          f' {ingredient["ingredient__measurement_unit"]}'),
                     align='L')

        result = pdf.output(dest='S').encode('latin-1')

        response = HttpResponse(
            result,
            content_type='application/pdf')
        response[
            'Content-Disposition'] = 'attachment; filename="shopping_list.pdf"'

        return response
