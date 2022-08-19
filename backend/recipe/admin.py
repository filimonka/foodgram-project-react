from django.contrib import admin
from django.contrib.auth import get_user_model

from .models import *

User = get_user_model()

class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name', 'author')
    search_fields = ('author', 'name', 'tags')
    readonly_fields = ('count_favourited',)

    def count_favourited(self, obj):
        return obj.favourite_dish.count()

"""
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name')
    search_fields = ('username', 'email')

"""

class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')




admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Tag)
#admin.site.unregister(User)
#admin.site.register(User, UserAdmin)
