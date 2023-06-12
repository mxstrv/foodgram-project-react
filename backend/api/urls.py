from django.urls import include, path
from rest_framework.routers import DefaultRouter
from djoser.views import TokenCreateView, TokenDestroyView

from .views import CustomUserViewSet


v1_router = DefaultRouter()
v1_router.register('users', CustomUserViewSet, basename='users')


auth_patterns = [
     path('login/', TokenCreateView.as_view(), name='user_login'),
     path('logout/', TokenDestroyView.as_view(), name='user_logout'),
 ]

urlpatterns = [
    path('', include(v1_router.urls)),
    path('auth/token/', include(auth_patterns)),
]
