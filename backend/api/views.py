from django.contrib.auth import get_user_model
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from rest_framework import filters, renderers, status
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import (IsAdminUser, IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from recipe.models import *

from .calculator import create_shopping_list
from .permissions import IsNotAuthor
from .serializers import *

User = get_user_model()


class PassthroughRenderer(renderers.BaseRenderer):
    media_type = 'text/plain'
    format = '.txt'

    def render(self, data, accepted_media_type=None, renderer_context=None):
        return data


class MyClassAdditionalActions(ModelViewSet):

    def additional_action(
        self,
        request,
        model,
        target_fieldname,
        kwarg_name,
        pk=None
    ):
        data = {
            'user': request.user,
            'target_fieldname': self.kwargs[kwarg_name]
        }
        data[target_fieldname] = data.pop('target_fieldname')
        if self.request.method == 'POST':
            connected_obj, created = model.objects.get_or_create(**data)
            if not created:
                return Response(
                    data={"errors": "Такая подписка уже существует"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            return Response(status=status.HTTP_201_CREATED)
        connected_obj = get_object_or_404(model, **data)
        connected_obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class MyUserViewSet(MyClassAdditionalActions, UserViewSet):
    permission_classes = [IsAuthenticatedOrReadOnly, ]

    @action(
        methods=['POST', 'DELETE'],
        detail=True,
        permission_classes=[IsNotAuthor, IsAuthenticated],
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
        return super().additional_action(
            request, model, target_fieldname, kwarg_name
        )

    @action(
        methods=['GET', ],
        detail=False,
        permission_classes=[IsAuthenticated, ]
    )
    def subscriptions(self, request):
        user = request.user
        queryset = User.objects.filter(cook__user=user).all().values()
        serializer = GetSubscriptionsSerializer(queryset, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)


class RecipeViewSet(MyClassAdditionalActions):
    serializer_class = RecipeSerializer
    queryset = Recipe.objects.all()
    pagination_class = PageNumberPagination
    page_size = 6
    permission_classes = [IsAuthenticatedOrReadOnly, IsAdminUser]
    filter_backends = (filters.SearchFilter,)
    filterset_fields = (
        '^author',
        '^tag',
        '^is_favorited',
        '^is_in_shopping_cart'
    )

    def perform_create(self, serializer):
        return serializer.save(author_id=self.request.user.id)

    @action(
        methods=['POST', 'DELETE'],
        detail=True,
        permission_classes=[IsAuthenticated, ],
        url_path='favorite'
    )
    def favorite(
        self,
        request,
        pk=None
    ):
        return self.additional_action(
            request,
            model=FavoriteRecipe,
            target_fieldname='recipe_id',
            kwarg_name='pk'
        )

    @action(
        methods=['POST', 'DELETE'],
        detail=True,
        permission_classes=[IsAuthenticated, ],
    )
    def shopping_cart(
        self,
        request,
        pk=None
    ):
        return self.additional_action(
            request,
            model=ShoppingCart,
            target_fieldname='recipe_id',
            kwarg_name='pk',
        )

    @action(
        methods=['GET'],
        detail=False,
        permission_classes=[IsAuthenticated, ],
        renderer_classes=[PassthroughRenderer, ]
    )
    def download_shopping_cart(self, request):
        user = request.user
        ingredients = RecipeIngredients.objects.prefetch_related(
            'shoppingcart'
            ).filter(
            recipe__cart_recipe__user=user
            ).values_list(
                'ingredient__name', 'amount', 'ingredient__measurement_unit'
            )
        ingredients = ([ingredient for ingredient in ingredients])
        print(ingredients)
        final_ingredient_count = create_shopping_list(ingredients)
        data_for_file = [
            f'{item} - {value[0]},{value[1]}'
            for item, value in final_ingredient_count.items()
        ]
        f = open('shopping_list.txt', 'w+')
        f.writelines(data_for_file)
        response = FileResponse(f, content_type='text/plain')
        response['Content-Disposition'] = (
            'attachment; filename="shopping_list.txt"'
        )
        return response


class TagViewSet(ReadOnlyModelViewSet):
    serializer_class = TagSerializer
    queryset = Tag.objects.all()


class IngredientViewSet(ReadOnlyModelViewSet):
    serializer_class = IngredientSerializer
    queryset = Ingredient.objects.all()
    filter_backends = (filters.SearchFilter,)
    filterset_fields = ('^name',)
