from django.contrib.auth import get_user_model
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from rest_framework import filters, status
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import (
    AllowAny, IsAuthenticated,
    IsAuthenticatedOrReadOnly
)
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from recipe.models import (
    FavoriteRecipe, Ingredient, Recipe,
    RecipeIngredients, ShoppingCart, Subscription, Tag
)

from .filters import IngredientFilter, RecipeFilter
from .permissions import IsNotAuthor, PutForbidden, UpdateForbidden
from .serializers import (
    GetSubscriptionsSerializer, IngredientSerializer,
    RecipeSerializer, RecipesForSubscriptions,
    TagSerializer
)
from .tools import create_shopping_list

User = get_user_model()


class AdditionalActionViewSet(ModelViewSet):

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
                    data={'errors': 'Такая подписка уже существует'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            return connected_obj
        connected_obj = get_object_or_404(model, **data)
        connected_obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class UserGetPostSubscriptionViewSet(AdditionalActionViewSet, UserViewSet):
    permission_classes = [AllowAny, UpdateForbidden]
    pagination_classes = (PageNumberPagination,)

    @action(
        methods=['POST', 'DELETE'],
        detail=True,
        permission_classes=[IsNotAuthor, IsAuthenticated],
        url_path='subscribe',
    )
    def subscribe(
        self,
        request,
        id=None
    ):
        result = self.additional_action(
            request,
            model=Subscription,
            target_fieldname='author_id',
            kwarg_name='id'
        )
        if isinstance(result, Subscription):
            serializer = GetSubscriptionsSerializer(result)
            return Response(
                data=serializer.data,
                status=status.HTTP_201_CREATED
            )
        return result

    @action(
        methods=['GET', ],
        detail=False,
        permission_classes=[IsAuthenticated, ],
    )
    def subscriptions(self, request):
        user = request.user
        queryset = Subscription.objects.filter(user=user).all()
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = GetSubscriptionsSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = GetSubscriptionsSerializer(queryset, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)


class RecipeViewSet(AdditionalActionViewSet):
    serializer_class = RecipeSerializer
    queryset = Recipe.objects.all()
    pagination_classes = (PageNumberPagination, )
    permission_classes = [IsAuthenticatedOrReadOnly, PutForbidden]
    filter_backends = (DjangoFilterBackend, filters.SearchFilter,)
    filterset_class = RecipeFilter
    search_fields = (
        '^ingredients__ingredient_name',
    )

    def perform_create(self, serializer):
        return serializer.save(author_id=self.request.user.id)

    # add/delete favorite
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
        result = self.additional_action(
            request,
            model=FavoriteRecipe,
            target_fieldname='recipe_id',
            kwarg_name='pk',
        )
        if isinstance(result, FavoriteRecipe):
            serializer = RecipesForSubscriptions(result.recipe)
            return Response(
                data=serializer.data,
                status=status.HTTP_201_CREATED
            )
        return result

    # add/delete shopping_cart
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
        result = self.additional_action(
            request,
            model=ShoppingCart,
            target_fieldname='recipe_id',
            kwarg_name='pk',
        )
        if isinstance(result, Subscription):
            serializer = RecipesForSubscriptions(result.recipe)
            return Response(
                data=serializer.data,
                status=status.HTTP_201_CREATED
            )
        return result

    # download shopping_cart
    @action(
        methods=['GET'],
        detail=False,
        permission_classes=[IsAuthenticated, ],
    )
    def download_shopping_cart(self, request):
        user = request.user
        ingredients = RecipeIngredients.objects.prefetch_related(
            'shoppingcart').filter(
                recipe__cart_recipe__user=user).values_list(
                    'ingredient__name',
                    'amount',
                    'ingredient__measurement_unit',
                )
        ingredients = [ingredient for ingredient in ingredients]
        final_ingredient_count = create_shopping_list(ingredients)
        text = [
            f'{name}: {value[0]}{value[1]}'
            for name, value
            in final_ingredient_count.items()
        ]
        text = '\n'.join(text)
        return FileResponse(
            text,
            as_attachment=True,
            filename='shopping_list.txt',
            content_type='text/plain'
        )


class TagViewSet(ReadOnlyModelViewSet):
    serializer_class = TagSerializer
    queryset = Tag.objects.all()
    pagination_class = None


class IngredientViewSet(ReadOnlyModelViewSet):
    serializer_class = IngredientSerializer
    queryset = Ingredient.objects.all()
    filter_backends = (DjangoFilterBackend, filters.SearchFilter,)
    filterset_class = IngredientFilter
    search_fields = ('^name',)
    pagination_class = None
