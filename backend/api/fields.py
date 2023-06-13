import base64

from django.core.files.base import ContentFile
from rest_framework import serializers


class Base64ImageField(serializers.ImageField):
    """
    Переопределение функции для работы с изображениями в Base64.
    """
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            file_formatting, image_b64 = data.split(';base64,')
            ext = file_formatting.split('/')[-1]
            data = ContentFile(base64.b64decode(image_b64), name='temp.' + ext)

        return super().to_internal_value(data)
