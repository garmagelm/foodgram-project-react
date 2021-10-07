from django_filters import rest_framework as filters
from rest_framework.filters import SearchFilter

from .models import Recipe


class IngredientNameFilter(SearchFilter):
    search_param = 'name'


class RecipeFilter(filters.FilterSet):
    is_favorited = filters.BooleanFilter(method='get_favorite',
                                         label='Favourited')
    is_in_shopping_cart = filters.BooleanFilter(method='get_shopping',
                                                label='Is in shopping list')
    tags = filters.AllValuesMultipleFilter(field_name='recipetag__tag__slug',
                                           label='Tags')

    class Meta:
        model = Recipe
        fields = ['is_favorited', 'author', 'tags', 'is_in_shopping_cart']

    def get_favorite(self, queryset, name, value):
        if value:
            return Recipe.objects.filter(in_favorite__user=self.request.user)
        return Recipe.objects.all()

    def get_shopping(self, queryset, name, value):
        if value:
            return Recipe.objects.filter(shoppinglist__user=self.request.user)
        return Recipe.objects.all()
