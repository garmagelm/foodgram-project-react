import django_filters as filters

from .models import Ingredient, Recipe, Purchase, Favorite


class IngredientNameFilter(filters.FilterSet):
    name = filters.CharFilter(field_name='name', lookup_expr='istartswith')

    class Meta:
        model = Ingredient
        fields = ('name', 'measurement_unit')


class RecipeFilter(filters.FilterSet):
    tags = filters.AllValuesMultipleFilter(field_name='tags__slug')

    class Meta:
        model = Recipe
        fields = ('author', 'tags')

    def get_queryset(self):
        queryset = Recipe.objects.all()
        is_in_shopping_cart = self.request.query_params.get(
            "is_in_shopping_cart"
        )
        is_favorited = self.request.query_params.get("is_favorited")
        cart = Purchase.objects.filter(user=self.request.user.id)
        favorite = Favorite.objects.filter(user=self.request.user.id)

        if is_in_shopping_cart == "true":
            queryset = queryset.filter(purchase__in=cart)
        elif is_in_shopping_cart == "false":
            queryset = queryset.exclude(purchase__in=cart)
        if is_favorited == "true":
            queryset = queryset.filter(favorites__in=favorite)
        elif is_favorited == "false":
            queryset = queryset.exclude(favorites__in=favorite)
        return queryset.all()
