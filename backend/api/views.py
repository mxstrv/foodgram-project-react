from rest_framework import viewsets

from users.models import CustomUser
from .permissions import IsAuthenticatedOrReadOnlyForProfile
from .serializers import UserSerializer


class UserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    permission_classes = [IsAuthenticatedOrReadOnlyForProfile, ]
    serializer_class = UserSerializer

