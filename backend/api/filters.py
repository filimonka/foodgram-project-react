import django_filters.rest_framework as filters
from django.contrib.auth import get_user_model

from recipe.models import Ingredient, Recipe, Tag

User = get_user_model()


class RecipeFilter(filters.FilterSet):
    tags = filters.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        queryset=Tag.objects.all(),
        to_field_name='slug')
    is_favorited = filters.BooleanFilter(method='get_is_favorited')
    is_in_shopping_cart = filters.BooleanFilter(
        method='get_is_in_shopping_cart'
    )
    author = filters.ModelChoiceFilter(
        field_name='author',
        to_field_name='id',
        queryset=User.objects.all())

    class Meta:
        Model = Recipe
        fields = [
            'tags',
            'author',
            'is_favorited',
            'is_in_shopping_cart',
        ]

    def get_is_favorited(self, queryset, name, value):
        if value:
            return queryset.filter(
                favorite_dish__user=self.request.user
            )
        return queryset

    def get_is_in_shopping_cart(self, queryset, name, value):
        if value:
            return queryset.filter(
                cart_recipe__user=self.request.user
            )
        return queryset


class IngredientFilter(filters.FilterSet):
    name = filters.CharFilter(lookup_expr='startswith')

    class Meta:
        model = Ingredient
        fields = {'name', 'measurement_unit'}
