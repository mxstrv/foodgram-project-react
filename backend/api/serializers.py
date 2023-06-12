from django.core.validators import RegexValidator
from rest_framework import serializers
from users.models import CustomUser


class UserSerializer(serializers.ModelSerializer):
    """ Сериализатор для работы с пользователем"""
    # TODO Добавить подписку на других пользователей
    first_name = serializers.CharField(max_length=150, required=True)
    last_name = serializers.CharField(max_length=150, required=True)
    email = serializers.CharField(max_length=254, required=True)
    username = serializers.CharField(max_length=150, required=True, validators=[
        RegexValidator(
            regex=r'^[\w.@+-]+',
            message='Неподходящий формат имени пользователя')])

    class Meta:
        model = CustomUser
        fields = [
            "email",
            "id",
            "username",
            "first_name",
            "last_name",
            "password",
        ]
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        """ Создание нового пользователя."""
        user = CustomUser(
            email=validated_data['email'],
            username=validated_data['username'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
        )
        user.set_password(validated_data['password'])
        user.save()
        return user
