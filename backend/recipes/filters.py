from django_filters import rest_framework as filters
from rest_framework.filters import SearchFilter

from .models import Recipe, User


class IngredientNameFilter(SearchFilter):
    search_param = 'name'


class RecipeFilter(filters.FilterSet):
    tags = filters.AllValuesMultipleFilter(field_name='tags__slug')
    authot = filters.ModelChoiceFilter(queryset=User.objects.all())
    is_favorited = filters.BooleanFilter(method='get_favorite')
    is_in_shopping_cart = filters.BooleanFilter(method='get_shopping')

    class Meta:
        model = Recipe
        fields = ('author', 'tags', 'is_favorited', 'is_in_shopping_cart')

    def get_favorite(self, queryset, name, value):
        if value:
            return Recipe.objects.filter(favorites__user=self.request.user)
        return Recipe.objects.all()

    def get_shopping(self, queryset, name, value):
        if value:
            return Recipe.objects.filter(purchase__user=self.request.user)
        return Recipe.objects.all()
