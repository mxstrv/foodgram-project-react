from rest_framework.filters import SearchFilter
from django_filters import rest_framework as filters

from recipes.models import Recipe, Tag


class IngredientSearch(SearchFilter):
    """ Поиск по ингредиентам. """
    search_param = 'name'


class RecipeFilter(filters.FilterSet):
    is_favorited = filters.BooleanFilter(
        method='get_favorite')
    is_in_shopping_cart = filters.BooleanFilter(
        method='get_is_in_shopping_cart')
    author = filters.CharFilter()
    tags = filters.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        queryset=Tag.objects.all(),
        to_field_name='slug',
        label='Tags'
    )

    class Meta:
        model = Recipe
        fields = [
            'author',
            'tags',
            'is_favorited',
            'is_in_shopping_cart'
        ]

    def get_favorite(self, queryset, value, _):
        if value:
            return queryset.filter(favorite_recipes__user=self.request.user)
        return queryset

    def get_is_in_shopping_cart(self, queryset, value, _):
        if value:
            return queryset.filter(shopping_cart__user=self.request.user)
        return queryset
