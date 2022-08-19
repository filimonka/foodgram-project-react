from django.urls import path, include
from rest_framework.routers import SimpleRouter

from .views import *


app_name = 'api'

router = SimpleRouter()

router.register('recipes', RecipeViewSet)
router.register('users', MyUserViewSet)
router.register('tags', TagViewSet)
router.register('ingredients', IngredientViewSet)
"""
router.register('download_shopping_cart', viewsets.Two)

"""

urlpatterns = [
    path('', include(router.urls)),
    path('', include('djoser.urls')),    
    path('auth/', include('djoser.urls.authtoken')),
]
