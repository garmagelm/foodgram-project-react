from django.contrib import admin

from .models import (Favorite, Ingredient, IngredientRecipe, Recipe, RecipeTag,
                     ShoppingCart, Tag)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'slug')


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'measurement_unit')
    list_filter = ['name']
    search_fields = ('name',)


class IngredientRecipeInline(admin.TabularInline):
    model = IngredientRecipe
    min_num = 1
    extra = 1


class RecipeTagInline(admin.TabularInline):
    model = RecipeTag
    min_num = 1
    extra = 0


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'author', 'favorited_by')
    list_filter = ['name', 'author', 'tags']
    inlines = (IngredientRecipeInline, RecipeTagInline)

    def favorited_by(self, obj):
        return obj.favorited_by.all().count()


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('pk', 'user', 'recipe')


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ('pk', 'user', 'recipe')
