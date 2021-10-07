from django.contrib.auth import get_user_model
from django.db.models import F

from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from users.serializers import CustomUserSerializer

from .models import (Favorite, Ingredient, IngredientForRecipe, Purchase,
                     Recipe, Tag)

User = get_user_model()


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = (
            'id',
            'name',
            'color',
            'slug',
        )


class FavoriteSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        source='recipe.id', read_only=True
    )
    name = serializers.CharField(source='recipe.name', read_only=True)
    image = Base64ImageField(source='recipe.image', read_only=True)
    cooking_time = serializers.IntegerField(
        source='recipe.cooking_time', read_only=True
    )

    class Meta:
        model = Favorite
        fields = (
            'id',
            'name',
            'image',
            'cooking_time',
        )


class PurchaseSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        source='recipe.id', read_only=True
    )
    name = serializers.CharField(source='recipe.name', read_only=True)
    image = Base64ImageField(source='recipe.image', read_only=True)
    cooking_time = serializers.IntegerField(
        source='recipe.cooking_time', read_only=True
    )

    class Meta:
        model = Purchase
        fields = (
            'id',
            'name',
            'image',
            'cooking_time',
        )


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = '__all__'


class IngredientForRecipeSerializer(serializers.ModelSerializer):
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )
    id = serializers.ReadOnlyField(source='ingredient.id')

    class Meta:
        model = IngredientForRecipe
        fields = ('id', 'name', 'measurement_unit', 'amount')


class IngredientForRecipeCreate(IngredientForRecipeSerializer):
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())
    amount = serializers.IntegerField()

    class Meta:
        model = IngredientForRecipe
        fields = ('id', 'amount')


class RecipeSerializer(serializers.ModelSerializer):
    author = CustomUserSerializer(read_only=True)
    ingredients = IngredientForRecipeCreate(many=True)
    tags = serializers.PrimaryKeyRelatedField(queryset=Tag.objects.all(),
                                              many=True)
    cooking_time = serializers.IntegerField()
    image = Base64ImageField(max_length=None, use_url=True)

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients', 'name',
                  'image', 'text', 'cooking_time')

    def validate_ingredients(self, data):
        ingredients = self.initial_data.get('ingredients')
        if not ingredients:
            raise ValidationError('Нужно выбрать минимум 1 ингридиент!')
        for ingredient in ingredients:
            if int(ingredient['amount']) <= 0:
                raise ValidationError('Количество должно быть положительным!')
        return data

    def validate_cooking_time(self, data):
        if data <= 0:
            raise ValidationError('Время готовки не может быть'
                                  ' отрицательным числом или нулем!')
        return data

    def create(self, validated_data):
        author = self.context.get('request').user
        tags_data = validated_data.pop('tags')
        ingredients_data = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(author=author, **validated_data)
        self.ingredients_recipe(ingredients_data, recipe)
        recipe.tags.set(tags_data)
        return recipe

    def ingredients_recipe(self, ingredients, recipe):
        for ingredient in ingredients:
            ingredient_id = ingredient['id']
            amount = ingredient['amount']
            if IngredientForRecipe.objects.filter(
                recipe=recipe, ingredient=ingredient_id
            ).exists():
                amount += F('amount')
            IngredientForRecipe.objects.update_or_create(
                recipe=recipe, ingredient=ingredient_id,
                defaults={'amount': amount})

    def update(self, recipe, validated_data):
        recipe.name = validated_data.get('name', recipe.name)
        recipe.text = validated_data.get('text', recipe.text)
        recipe.cooking_time = validated_data.get('cooking_time',
                                                 recipe.cooking_time)
        recipe.image = validated_data.get('image', recipe.image)
        if 'ingredients' in self.initial_data:
            ingredients = validated_data.pop('ingredients')
            recipe.ingredients.clear()
            self.ingredients_recipe(ingredients, recipe)
        if 'tags' in self.initial_data:
            tags_data = validated_data.pop('tags')
            recipe.tags.set(tags_data)
        recipe.save()
        return recipe

    def to_representation(self, recipe):
        data = RecipeReadSerializer(recipe, context={'request':
                                    self.context.get('request')}).data
        return data


class RecipeReadSerializer(RecipeSerializer):
    tags = TagSerializer(read_only=True, many=True)
    author = CustomUserSerializer(read_only=True)
    ingredients = serializers.SerializerMethodField()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    def get_ingredients(self, obj):
        ingredients = IngredientForRecipe.objects.filter(recipe=obj)
        return IngredientForRecipeSerializer(ingredients, many=True).data

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return Favorite.objects.filter(user=request.user, recipe=obj).exists()

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return Purchase.objects.filter(
            user=request.user, recipe=obj).exists()

    class Meta:
        model = Recipe
        fields = '__all__'
