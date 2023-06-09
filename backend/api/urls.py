from django.urls import include, path
from rest_framework.routers import DefaultRouter

# from .views import ...


v1_router = DefaultRouter()
v1_router.register('users', UserViewSet, basename='users')


auth_patterns = [
    path('login/', TokenReceive.as_view(), name='user_login'),
    path('logout/', TokenDelete.as_view(), name='user_logout'),
]

urlpatterns = [
    path('', include(v1_router.urls)),
    path('/auth/token/', include(auth_patterns)),
]
