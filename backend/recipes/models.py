from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import UniqueConstraint

User = get_user_model()


class Ingredient(models.Model):
    name = models.CharField(max_length=200,
                            verbose_name="Ingredient's name")
    measurement_unit = models.CharField(max_length=200,
                                        verbose_name='Unit')

    class Meta:
        ordering = ('name',)
        verbose_name = 'Ingredient'
        verbose_name_plural = 'Ingredients'

    def __str__(self):
        return self.name


class Tag(models.Model):
    RED = 'RED'
    ORANGE = 'ORANGE'
    YELLOW = 'YELLOW'
    GREEN = 'GREEN'
    BLUE = 'BLUE'
    PURPLE = 'PURPLE'

    COLORS_CHOICES = (
        (RED, 'Red'),
        (ORANGE, 'Orange'),
        (YELLOW, 'Yellow'),
        (GREEN, 'Green'),
        (BLUE, 'Blue'),
        (PURPLE, 'Purple')
    )
    name = models.CharField(max_length=200, unique=True,
                            verbose_name='Tag')
    color = models.TextField(
        'Color',
        choices=COLORS_CHOICES,
        blank=True,)
    slug = models.SlugField(
        max_length=200,
        unique=True,
        verbose_name='Slug')

    class Meta:
        ordering = ('name',)
        verbose_name = 'Tag'
        verbose_name_plural = 'Tags'

    def __str__(self):
        return self.name


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name="Recipe's author",
    )
    name = models.CharField(
        max_length=200,
        verbose_name="Recipe's name",
    )
    image = models.ImageField(
        upload_to='recipes/',
        verbose_name="Dish's image"
    )
    text = models.TextField(
        verbose_name='Recipe Description',
        help_text='Add a description of the recipe',
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='IngredientRecipe',
        verbose_name='Ingredients',
    )
    tags = models.ManyToManyField(
        Tag,
        related_name='recipes',
        verbose_name='Tags',
    )
    cooking_time = models.PositiveIntegerField(
        validators=[MinValueValidator(1,
                    message='Minimum cooking time is 1 minute')],
        verbose_name='Cooking time in minutes',
        help_text='Specify the cooking time in minutes',
    )
    pub_date = models.DateTimeField(
        auto_now_add=True, verbose_name='Date of publication'
    )

    class Meta:
        verbose_name = 'Recipe'
        verbose_name_plural = 'Recipes'
        ordering = ('-id',)

    def __str__(self):
        return self.name


class IngredientRecipe(models.Model):
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.PROTECT,
        verbose_name='The ingredient used in the recipe',
    )
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, verbose_name='Recipe'
    )
    amount = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1)],
        verbose_name='Ingredient Quantity'
    )

    class Meta:
        constraints = [UniqueConstraint(fields=['ingredient', 'recipe'],
                       name='unique_ingredient_in_recipe')]
        verbose_name = 'Ingredient'
        verbose_name_plural = 'Ingredients'


class RecipeTag(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE,
                            verbose_name='Тег')

    class Meta:
        constraints = [UniqueConstraint(fields=['tag', 'recipe'],
                       name='unique_recipe_tag')]
        verbose_name = 'Tag'
        verbose_name_plural = 'Tags'

    def __str__(self):
        return "Recipe's tag"


class Favorite(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorite',
        verbose_name='User',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorited_by',
        verbose_name='Recipe',
    )

    class Meta:
        constraints = [models.UniqueConstraint(fields=['user', 'recipe'],
                       name='unique_recipe_in_user_favorite')]
        ordering = ('-id',)
        verbose_name = 'Favorite'
        verbose_name_plural = 'Favorite'


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='shopping_cart',
        verbose_name='User',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Recipe in the shopping list',
    )

    class Meta:
        constraints = [UniqueConstraint(fields=['user', 'recipe'],
                       name='unique_recipe_in_user_shopping_cart')]
        ordering = ('-id',)
        verbose_name = 'Shopping list'
        verbose_name_plural = 'Shopping lists'
