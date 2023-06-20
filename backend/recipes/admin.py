from django.contrib import admin

from .models import Recipe, Favorite, Ingredient, ShoppingCart, Tag


class RecipeAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'name',
        'author',
    ]
    search_fields = ['name', 'author__username']
    list_filter = ['tags']
    empty_value_display = '-пусто-'


class FavoriteAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'user',
        'recipe'
    ]
    search_fields = ['user__username', 'user__email']
    empty_value_display = '-пусто-'


class IngredientAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'name',
        'measurement_unit'
    ]
    search_fields = ['name']
    empty_value_display = '-пусто-'


class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'user',
        'recipe'
    ]
    search_fields = ['user__username', 'user__email']
    empty_value_display = '-пусто-'


class TagAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'name',
        'color',
        'slug'
    ]
    search_fields = ['name', 'slug']
    empty_value_display = '-пусто-'


admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Favorite, FavoriteAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(ShoppingCart, ShoppingCartAdmin)
admin.site.register(Tag, TagAdmin)
