from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny
from djoser.views import UserViewSet

from recipes.models import Tag
from users.models import CustomUser
from .permissions import IsAuthenticatedOrReadOnlyForProfile
from .serializers import UserSerializer, TagSerializer


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
    permission_classes = [AllowAny, ]
    http_method_names = ['get']
    serializer_class = TagSerializer
    pagination_class = None
