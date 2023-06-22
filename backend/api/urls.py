from django.urls import include, path
from djoser.views import TokenCreateView, TokenDestroyView
from rest_framework.routers import DefaultRouter

from .views import (CustomUserViewSet, TagViewSet,
                    RecipeViewSet, IngredientViewSet)

router = DefaultRouter()
router.register('users', CustomUserViewSet, basename='users')
router.register('tags', TagViewSet, basename='tags')
router.register('recipes', RecipeViewSet, basename='recipes')
router.register('ingredients', IngredientViewSet, basename='ingredients')


auth_patterns = [
    path('login/', TokenCreateView.as_view(), name='user_login'),
    path('logout/', TokenDestroyView.as_view(), name='user_logout'),
]

urlpatterns = [
    path('', include(router.urls)),
    path('auth/token/', include(auth_patterns)),
]
