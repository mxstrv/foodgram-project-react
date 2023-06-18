from rest_framework.filters import SearchFilter


class IngredientSearch(SearchFilter):
    """ Поиск по ингредиентам. """
    search_param = 'name'
