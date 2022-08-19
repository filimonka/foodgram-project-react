import base64

from django.core.files.base import ContentFile
from rest_framework.fields import ImageField
from rest_framework.validators import ValidationError


class Base64ToFile(ImageField):
    def to_internal_value(self, data):

        if isinstance(data, str):
            if 'data:' in data and ';base64,' in data:
                header, file_data = data.split(';base64,')
            try:
                decoded_file = base64.b64decode(file_data)
            except TypeError:
                raise ValidationError(
                    'Изображение передано в неизвестном формате'
                )
        name, file_ext = header.split('/')
        file_name = f'{name[5:]}.{file_ext}'
        data = ContentFile(decoded_file, name=file_name)
        return super(Base64ToFile, self).to_internal_value(data)
