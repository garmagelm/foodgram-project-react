from django.contrib.auth import get_user_model

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
    id = serializers.IntegerField(write_only=True, min_value=1)
    amount = serializers.IntegerField(write_only=True)


class RecipeSerializer(serializers.ModelSerializer):
    tags = serializers.PrimaryKeyRelatedField(queryset=Tag.objects.all(),
                                              many=True)
    image = Base64ImageField(max_length=None, use_url=True)
    ingredients = IngredientForRecipeCreate(many=True)

    class Meta:
        model = Recipe
        fields = ('ingredients', 'tags', 'image', 'name', 'text',
                  'cooking_time')

    def validate_ingredients(self, data):
        ingredients = self.initial_data.get('ingredients')
        not_unique_ingredients = []
        for ingredient in ingredients:
            if abs(int(ingredient['amount'])) != int(ingredient['amount']):
                raise ValidationError(
                    'Количество не может быть отрицательным'
                )
            if int(ingredient['amount']) < 1:
                raise ValidationError(
                    'Минимальное количество для ингредиента: 1'
                )
            not_unique_ingredients.append(ingredient['id'])
        unique_ingredients = set(not_unique_ingredients)
        if len(not_unique_ingredients) > len(unique_ingredients):
            raise ValidationError(
                'Ингредиенты не должны повторяться'
            )
        return data

    def add_recipe_ingredient(self, ingredients, recipe):
        for ingredient in ingredients:
            IngredientForRecipe.objects.create(
                ingredient_id=ingredient.get('id'),
                recipe=recipe,
                amount=ingredient.get('amount'),
            )

    def create(self, validated_data):
        request = self.context.get('request')
        ingredients = validated_data.pop('ingredients')
        tags_data = validated_data.pop('tags')
        recipe = Recipe.objects.create(author=request.user, **validated_data)
        self.add_recipe_ingredients(ingredients, recipe)
        recipe.tags.set(tags_data)
        return recipe

    def update(self, instance, validated_data):
        instance.image = validated_data.get('image', instance.image)
        instance.name = validated_data.get('name', instance.name)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get(
            'cooking_time', instance.cooking_time
        )
        instance.tags.clear()
        tags = self.initial_data.get('tags')
        instance.tags.set(tags)
        IngredientForRecipe.objects.filter(recipe=instance).all().delete()
        ingredients = validated_data.get('ingredients')
        self.add_recipe_ingredient(ingredients, instance)
        instance.save()
        return instance

    def to_representation(self, instance):
        return RecipeReadSerializer(instance).data


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
