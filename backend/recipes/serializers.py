from django.contrib.auth import get_user_model
from django.db.models import F

from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.validators import UniqueTogetherValidator
from users.serializers import CustomUserSerializer

from .models import (Favorite, Ingredient, IngredientForRecipe, Purchase,
                     Recipe, Tag)

User = get_user_model()


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name', 'color', 'slug']


class FavoriteSerializer(serializers.ModelSerializer):
    user = serializers.IntegerField(source='user.id')
    recipe = serializers.IntegerField(source='recipe.id')

    class Meta:
        model = Favorite
        fields = ['user', 'recipe']
        validators = [UniqueTogetherValidator(
            queryset=Favorite.objects.all(),
            fields=['user', 'recipe'],
            message=('Вы уже добавли рецепт в избранное!')
        )]


class PurchaseSerializer(serializers.ModelSerializer):
    user = serializers.IntegerField(source='user.id')
    recipe = serializers.IntegerField(source='recipe.id')

    class Meta:
        model = Purchase
        fields = '__all__'
        validators = [UniqueTogetherValidator(
            queryset=Purchase.objects.all(),
            fields=['user', 'recipe'],
            message=('Вы уже добавили рецепт в список покупок!')
        )]


class IngredientSerializer(serializers.ModelSerializer):
    name = serializers.ReadOnlyField()
    measurement_unit = serializers.ReadOnlyField()

    class Meta:
        model = Ingredient
        fields = ['id', 'name', 'measurement_unit']


class IngredientForRecipeSerializer(serializers.ModelSerializer):
    name = serializers.ReadOnlyField(source='ingredient.name', read_only=True)
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit', read_only=True)

    class Meta:
        model = IngredientForRecipe
        fields = ['id', 'name', 'amount', 'measurement_unit']


class IngredientForRecipeCreate(IngredientForRecipeSerializer):
    id = serializers.IntegerField(write_only=True)
    amount = serializers.IntegerField(write_only=True)

    def validate_amount(self, amount):
        if amount < 1:
            raise serializers.ValidationError(
                'Убедитесь, что это значение больше 0.'
            )
        return amount


class RecipeSerializer(serializers.ModelSerializer):
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    tags = serializers.PrimaryKeyRelatedField(queryset=Tag.objects.all(),
                                              many=True)
    author = CustomUserSerializer(read_only=True)
    image = Base64ImageField(max_length=None, use_url=True)
    ingredients = IngredientForRecipeCreate(many=True)

    class Meta:
        model = Recipe
        fields = [
            'id', 'tags', 'author', 'ingredients', 'is_favorited',
            'is_in_shopping_cart', 'name', 'image', 'text',
            'cooking_time', 'pub_date'
        ]

    def validate_ingredients(self, data):
        ingredients = self.initial_data.get('ingredients')
        ingredients_set = set()
        if not ingredients:
            raise ValidationError('Нужно выбрать хотя бы один ингредиент!')
        for ingredient in ingredients:
            if int(ingredient['amount']) <= 0:
                raise ValidationError('Количество должно быть положительными!')
            if ingredient in ingredients_set:
                raise ValidationError('Вы уже добавили этот ингредиент!')
            ingredients_set.add(ingredient)
        return data

    def add_recipe_ingredients(self, ingredients, recipe):
        for ingredient in ingredients:
            ingredient_id = ingredient['id']
            amount = ingredient['amount']
            if (IngredientForRecipe.objects.filter(
                    recipe=recipe, ingredient=ingredient_id).exists()):
                amount += F('amount')
            IngredientForRecipe.objects.update_or_create(
                recipe, ingredient=ingredient_id, defaults={'amount': amount})

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return Favorite.objects.filter(user=request.user, recipe=obj).exists()

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return Purchase.objects.filter(user=request.user, recipe=obj).exists()

    def create(self, validated_data):
        request = self.context.get('request')
        ingredients = validated_data.pop('ingredients')
        tags_data = validated_data.pop('tags')
        recipe = Recipe.objects.create(author=request.user, **validated_data)
        self.add_recipe_ingredients(ingredients, recipe)
        recipe.tags.set(tags_data)
        return recipe

    def update(self, instance, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags_data = validated_data.pop('tags')
        recipe = Recipe.objects.filter(id=instance.id)
        recipe.update(**validated_data)
        ingredients_instance = IngredientForRecipe.objects.values_list(
            'ingredient')
        self.add_recipe_ingredients(ingredients, recipe)
        if validated_data.get('image') is not None:
            instance.image = validated_data.get('image', instance.image)
        instance.ingredients.remove(*ingredients_instance)
        instance.tags.set(tags_data)
        return instance


class RecipeReadSerializer(RecipeSerializer):
    tags = TagSerializer(read_only=True, many=True)
    author = CustomUserSerializer(read_only=True)
    ingredients = serializers.SerializerMethodField()

    def get_ingredients(self, obj):
        ingredients = IngredientForRecipe.objects.filter(recipe=obj)
        return IngredientForRecipeSerializer(ingredients, many=True).data
