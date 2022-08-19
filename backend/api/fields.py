import base64
from django.core.files.base import ContentFile
from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.fields import ImageField
from rest_framework.validators import ValidationError
from rest_framework.decorators import action
from rest_framework.response import Response


class Base64ToFile(ImageField):
    def to_internal_value(self, data):

        if isinstance(data, str):
            if 'data:' in data and ';base64,' in data:
                header, file_data = data.split(';base64,')
            try:                
                decoded_file = base64.b64decode(file_data)
            except TypeError:
                raise ValidationError('Изображение передано в неизвестном формате')
        name, file_ext = header.split('/')
        file_name = f'{name[5:]}.{file_ext}' 
        data = ContentFile(decoded_file, name=file_name)
        return super(Base64ToFile, self).to_internal_value(data)


class MyClassAdditionalActions(viewsets.ModelViewSet):

    @action(
        methods=['POST', 'DELETE'],
        detail=True
    )
    def additional_action(self, request, model, target_fieldname, kwarg_name, pk=None):
        data = {
            'user': self.request.user,
            'target_fieldname': self.kwargs[kwarg_name]
        }
        data[target_fieldname] = data.pop('target_fieldname')
        if self.request.method == 'POST':
            connected_obj, created = model.objects.get_or_create(**data)
            if created == False:
                return Response(
                    data={"errors": "Такая подписка уже существует"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            return Response(status=status.HTTP_201_CREATED)
        connected_obj = get_object_or_404(model, **data)
        connected_obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)




    
