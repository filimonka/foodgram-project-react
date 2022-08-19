from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404, get_list_or_404
from rest_framework import filters, status
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny, IsAuthenticatedOrReadOnly, IsAdminUser
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from djoser.views import UserViewSet

from recipe.models import *
from .serializers import *
from .fields import MyClassAdditionalActions
from .permissions import IsNotAuthor


User = get_user_model()


class MyClassAdditionalActions(ModelViewSet):

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
    
    @action(
        methods=['GET'],
        detail=False
    )
    def get_filtered(self, request, filter):
        return Recipe.objects.filter(filter).get_list_or_404()


class MyUserViewSet(MyClassAdditionalActions, UserViewSet):

    @action(
        methods=['POST', 'DELETE'],
        detail=True,
        permission_classes=[IsNotAuthor],
        url_path='subscribe',
    )
    def additional_action(
        self,
        request,
        model=Subscription,
        target_fieldname='author_id',
        kwarg_name='id',
        id=None
    ):
        return super().additional_action(request, model, target_fieldname, kwarg_name)

    @action(
        methods=['GET',],
        detail=False
    )
    def subscriptions(self, request):
        user = request.user
        authors = User.objects.filter(cook__user=user).all().values()
        return Response(data=authors, status=status.HTTP_200_OK)
        

class RecipeViewSet(MyClassAdditionalActions):
    serializer_class = RecipeSerializer
    queryset = Recipe.objects.all()
    pagination_class = PageNumberPagination
    page_size = 6
    #filter_backends = (filters.SearchFilter)
    #filterset_fields = ('^author', '^tag', '^is_favorited', '^is_in_shopping_cart')

    def perform_create(self, serializer):
        return serializer.save(author_id=self.request.user.id)
    
    @action(
        methods=['POST', 'DELETE'],
        detail=True,
        url_path='favorite'
    )
    def additional_action(
        self,
        request,
        model=FavoriteRecipe,
        target_fieldname='recipe_id',
        kwarg_name='pk',
        pk=None
    ):
        return super().additional_action(request, model, target_fieldname, kwarg_name)

    
    @action(
        methods=['POST', 'DELETE'],
        detail=True,
        url_path='shopping_cart'
    )
    def additional_action(
        self,
        request,
        model=ShoppingCart,
        target_fieldname='recipe_id',
        pk=None
    ):
        return super().additional_action(request, model, target_fieldname, pk)


class TagViewSet(ModelViewSet):
    serializer_class = TagSerializer
    queryset = Tag.objects.all()


class IngredientViewSet(ModelViewSet):
    serializer_class = IngredientSerializer
    queryset = Ingredient.objects.all()
