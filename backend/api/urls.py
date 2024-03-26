from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.views import IngredientViewSet, RecipeViewSet, TagViewSet, UserViewSet
from users.views import (change_password_view, check_profile, login_view,
                         logout_view)

router = DefaultRouter()

router.register('users', UserViewSet, basename='users')

router.register('tags', TagViewSet, basename='tags')

router.register('ingredients', IngredientViewSet, basename='ingredients')

router.register('recipes', RecipeViewSet, basename='recipes')


urlpatterns = [
    path('users/me/', check_profile, name='me'),
    path('users/set_password/', change_password_view, name='change_password'),
    path('auth/token/login/', login_view, name='login'),
    path('auth/token/logout/', logout_view, name='logout'),
    path('', include(router.urls)),
]
