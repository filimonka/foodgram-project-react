from colorfield.fields import ColorField, ColorWidget
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin

from .models import Ingredient, Recipe, RecipeIngredients, Tag

User = get_user_model()


class RecipeIngredientInline(admin.StackedInline):
    model = RecipeIngredients


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
    formfield_overrides = {
      ColorField: {'widget': ColorWidget},
    }


class UserAdminWithNewFilters(UserAdmin):
    list_filter = ('username', 'email', 'first_name', 'last_name')


admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.unregister(User)
admin.site.register(User, UserAdminWithNewFilters)
