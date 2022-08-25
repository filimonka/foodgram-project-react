import collections

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from djoser.serializers import UserCreateSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from recipe.models import (
    FavoriteRecipe, Ingredient, Recipe,
    RecipeIngredients, ShoppingCart, Subscription, Tag
)

User = get_user_model()


class UserCreateSerializer(UserCreateSerializer):
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = ('email', 'username', 'first_name', 'last_name', 'password')


class UserGetSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'is_subscribed'
        )

    def get_is_subscribed(self, obj):
        if not isinstance(obj, User):
            user = obj.user
            author = obj.author
        else:
            author = obj
            user = self.context['request'].user
        if user.is_anonymous:
            return False
        return Subscription.objects.filter(
            user=user, author=author
        ).exists()


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = (
            'id',
            'name',
            'color',
            'slug'
        )


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = (
            'id',
            'name',
            'measurement_unit'
        )


class RecipeIngredientSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(),
        source='ingredient.id'
    )
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = RecipeIngredients
        fields = (
            'id',
            'name',
            'measurement_unit',
            'amount',
        )


class RecipeSerializer(serializers.ModelSerializer):
    author = UserGetSerializer(read_only=True)
    ingredients = RecipeIngredientSerializer(
        many=True,
        source='recipe_ingredient',
        required=True,
    )
    image = Base64ImageField()
    tags = TagSerializer(many=True, read_only=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'author',
            'name',
            'text',
            'image',
            'cooking_time',
            'tags',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
        )

    def get_is_favorited(self, obj):
        if self.context['request'].user.is_anonymous:
            return False
        return FavoriteRecipe.objects.filter(
            user=self.context['request'].user, recipe=obj
        ).exists()

    def get_is_in_shopping_cart(self, obj):
        if self.context['request'].user.is_anonymous:
            return False
        return ShoppingCart.objects.filter(
            user=self.context['request'].user, recipe=obj
        ).exists()

    def validate_tags(self, value):
        if not isinstance(value, collections.Iterable):
            raise ValidationError(
                'Tag передан в неверном формате'
            )
        queryset_values = Tag.objects.all().values_list(flat=True)
        for tag in value:
            if tag not in queryset_values:
                raise ValidationError(
                    f'Tag с id {tag} не найден, проверьте переданные данные'
                )
        return value

    def create(self, validated_data):
        if 'tags' not in self.initial_data:
            raise ValidationError('Необходимо добавить хотя бы один тэг')
        tags = self.initial_data.pop('tags')
        self.validate_tags(tags)
        ingredients = validated_data.pop('recipe_ingredient')
        recipe = Recipe.objects.create(
            **validated_data
        )
        all_ingredients = [
            RecipeIngredients(
                recipe=recipe,
                ingredient=ingredient['ingredient']['id'],
                amount=ingredient['amount']
            ) for ingredient in ingredients
        ]
        RecipeIngredients.objects.bulk_create(all_ingredients)
        recipe.tags.add(*tags)
        return recipe

    def update(self, instance, validated_data):
        if 'tags' in self.initial_data:
            instance.tags.clear()
            tags = self.initial_data.pop('tags')
            self.validate_tags(tags)
            instance.tags.add(*tags)
        ingredients = validated_data.pop('recipe_ingredient')
        RecipeIngredients.objects.filter(recipe_id=instance.id).delete()
        all_ingredients = [
            RecipeIngredients(
                recipe=instance,
                ingredient=ingredient['ingredient']['id'],
                amount=ingredient['amount']
            ) for ingredient in ingredients
        ]
        RecipeIngredients.objects.bulk_create(all_ingredients)
        return super().update(instance, validated_data)


class RecipesForSubscriptions(serializers.ModelSerializer):
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class GetSubscriptionsSerializer(UserGetSerializer):
    id = serializers.ReadOnlyField(source='author.id')
    email = serializers.ReadOnlyField(source='author.email')
    username = serializers.ReadOnlyField(source='author.username')
    first_name = serializers.ReadOnlyField(source='author.first_name')
    last_name = serializers.ReadOnlyField(source='author.last_name')
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = Subscription
        fields = (
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count',
        )

    def get_recipes(self, obj):
        instance = Recipe.objects.filter(
            author_id=obj.author.id
        ).all()
        serializer = RecipesForSubscriptions(instance, many=True)
        return serializer.data

    def get_recipes_count(self, obj):
        return Recipe.objects.filter(author_id=obj.author.id).count()


class FavoriteRecipeSerializer(serializers.ModelSerializer):

    class Meta:
        model = FavoriteRecipe
        fields = ('user', 'recipe')
