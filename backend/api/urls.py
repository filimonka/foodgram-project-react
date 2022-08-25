from django.urls import include, path
from rest_framework.routers import SimpleRouter

from .views import (
    IngredientViewSet, RecipeViewSet, TagViewSet,
    UserGetPostSubscriptionViewSet,
)

app_name = 'api'

router = SimpleRouter()

router.register('recipes', RecipeViewSet)
router.register('users', UserGetPostSubscriptionViewSet)
router.register('tags', TagViewSet)
router.register('ingredients', IngredientViewSet)


urlpatterns = [
    path('', include(router.urls)),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]
