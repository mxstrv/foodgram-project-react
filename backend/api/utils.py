from rest_framework import status
from rest_framework.response import Response


def instance_create_connection(request, instance, model_serializer):
    """
    Функция, отвечающая за добавление рецепта в избранное/список покупок.
    """
    serializer = model_serializer(
        data={'user': request.user.id, 'recipe': instance.id, },
        context={'request': request}
    )
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(serializer.data, status=status.HTTP_201_CREATED)


def instance_delete_connection(request, model, instance):
    """
    Функция, отвечающая за удаление рецепта из избранного/списка покупок.
    """
    model.objects.filter(user=request.user, recipe=instance).delete()
    return Response(status=status.HTTP_204_NO_CONTENT)
