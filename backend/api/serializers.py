from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from djoser.serializers import UserCreateSerializer
from rest_framework import serializers

from recipe.models import (FavoriteRecipe, Ingredient, Recipe,
                           RecipeIngredients, ShoppingCart, Subscription, Tag)
from .fields import Base64ToFile

User = get_user_model()


class UserCreateSerializer(UserCreateSerializer):
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = ('email', 'username', 'first_name', 'last_name', 'password')


class UserGetSerializer(serializers.ModelSerializer):
    username = serializers.CharField(required=False)
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
        if self.context['request'].user.is_anonymous:
            return False
        return Subscription.objects.filter(
            user=self.context['request'].user,
            author=obj).exists()


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
        required=True
    )
    image = Base64ToFile(use_url=True, required=True)
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
            user=self.context['request'].user,
            recipe=obj).exists()

    def get_is_in_shopping_cart(self, obj):
        if self.context['request'].user.is_anonymous:
            return False
        return ShoppingCart.objects.filter(
            user=self.context['request'].user,
            recipe=obj).exists()

    def validate_tags(self, value):
        if type(value) != list:
            raise ValidationError(
                'Поле тэг передано в неподходящем формате.'
                'Ожидаемый формат: list'
            )
        tag_id_list = Tag.objects.all().values_list('id', flat=True)
        for tag in value:
            if tag not in tag_id_list:
                raise ValidationError(
                    f'Тэг с id {tag} не найден, проверьте переданные данные'
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
            tags = self.initial_data.pop('tags')
            self.validate_tags(tags)
        ingredients = validated_data.pop('recipe_ingredient')
        instance.name = validated_data.get('name', instance.name)
        instance.author = validated_data.get('author', instance.author)
        instance.text = validated_data.get('text', instance.text)
        instance.image = validated_data.get('image', instance.image)
        instance.cooking_time = validated_data.get(
            'cooking_time',
            instance.cooking_time
        )
        instance.save()
        instance.tags.add(*tags)
        RecipeIngredients.objects.filter(recipe_id=instance.id).delete()
        all_ingredients = [
            RecipeIngredients(
                recipe=instance,
                ingredient=ingredient['ingredient']['id'],
                amount=ingredient['amount']
            ) for ingredient in ingredients
        ]
        RecipeIngredients.objects.bulk_create(all_ingredients)
        return instance


class RecipeShowSerializer(serializers.BaseSerializer):
    def to_representation(self, instance):
        return {
            'id': instance['id'],
            'name': instance['name'],
            'image': instance['image'],
            'cooking_time': instance['cooking_time']
        }


class SubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscription
        fields = ('author', 'user')

    def validate(self, data):
        if data['user'] == data['author']:
            raise serializers.ValidationError(
                'Нельзя подписаться на самого себя'
            )
        return data


class GetSubscriptionsSerializer(serializers.BaseSerializer):

    def to_representation(self, instance):
        return {
            'id': instance['id'],
            'email': instance['email'],
            'username': instance['username'],
            'first_name': instance['first_name'],
            'last_name': instance['last_name'],
            'is_subscribed': True,
            'recipes': RecipeShowSerializer(
                Recipe.objects.filter(author_id=instance['id']).all().values(),
                many=True
            ).data,
            'recipes_count': Recipe.objects.filter(
                author_id=instance['id']
            ).all().count()
        }


class FavoriteRecipeSerializer(serializers.ModelSerializer):

    class Meta:
        model = FavoriteRecipe
        fields = ('user', 'recipe')
