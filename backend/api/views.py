from django.shortcuts import get_object_or_404
from rest_framework.pagination import PageNumberPagination
from djoser.views import UserViewSet

from users.models import CustomUser
from .permissions import IsAuthenticatedOrReadOnlyForProfile
from .serializers import UserSerializer


class CustomUserViewSet(UserViewSet):
    queryset = CustomUser.objects.all()
    permission_classes = [IsAuthenticatedOrReadOnlyForProfile, ]
    serializer_class = UserSerializer
    pagination_class = PageNumberPagination

    def get_object(self):
        # Для GET запроса по id пользователя
        return get_object_or_404(CustomUser,
                                 id=self.kwargs.get('id'))
