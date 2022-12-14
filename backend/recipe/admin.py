from colorfield.fields import ColorField, ColorWidget
from django.forms import BaseInlineFormSet, ValidationError
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin

from .models import (
    FavoriteRecipe, Ingredient, Recipe, RecipeIngredients,
    ShoppingCart, Subscription, Tag
)

User = get_user_model()


class RecipeIngredientFormset(BaseInlineFormSet):
    def clean(self):
        super().clean()
        count = 0
        for form in self.forms:
            try:
                if form.cleaned_data:
                    count += 1
            except AttributeError:
                pass
            if count < 1:
                raise ValidationError(
                    'В рецепт нужно добавить хотя бы один ингредиент'
                )


class RecipeIngredientInline(admin.StackedInline):
    model = RecipeIngredients
    extra = 1
    formset = RecipeIngredientFormset


class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name', 'author')
    list_filter = ('author', 'name', 'tags')
    inlines = (RecipeIngredientInline, )
    readonly_fields = ('count_favorited',)

    def count_favorited(self, obj):
        return obj.favorite_dish.count()


class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')
    list_filter = ('name', )
    search_fields = ('name__startswith',)


class TagAdmin(admin.ModelAdmin):
    pass


class UserAdminWithNewFilters(UserAdmin):
    list_filter = ('username', 'email', 'first_name', 'last_name')


class RecipeIngredientsAdmin(admin.ModelAdmin):
    list_display = ('recipe', 'ingredient')
    list_filter = ('recipe', 'ingredient')


class FavoriteRecipeAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe')
    list_filter = ('user', 'recipe')


class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe')
    list_filter = ('user', 'recipe')


class SubscriptionsAdmin(admin.ModelAdmin):
    list_display = ('user', 'author')
    list_filter = ('user', 'author')


admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.unregister(User)
admin.site.register(User, UserAdminWithNewFilters)
admin.site.register(RecipeIngredients, RecipeIngredientsAdmin)
admin.site.register(FavoriteRecipe, FavoriteRecipeAdmin)
admin.site.register(ShoppingCart, ShoppingCartAdmin)
admin.site.register(Subscription, SubscriptionsAdmin)
