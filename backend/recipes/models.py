from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import UniqueConstraint

User = get_user_model()


class Ingredient(models.Model):
    name = models.CharField(max_length=200,
                            verbose_name='Название ингридиента')
    measurement_unit = models.CharField(max_length=200,
                                        verbose_name='Еденица измерения')

    class Meta:
        ordering = ('name',)
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

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
        (RED, 'Красный'),
        (ORANGE, 'Оранжевый'),
        (YELLOW, 'Желтый'),
        (GREEN, 'Зеленый'),
        (BLUE, 'Синий'),
        (PURPLE, 'Фиолетовый')
    )
    name = models.CharField(max_length=200, unique=True,
                            verbose_name='Тег')
    color = models.TextField(
        'Цвет',
        choices=COLORS_CHOICES,
        blank=True,)
    slug = models.SlugField(
        max_length=200,
        unique=True,
        verbose_name='Слаг')

    class Meta:
        ordering = ('name',)
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор рецепта',
    )
    name = models.CharField(
        max_length=200,
        verbose_name='Название рецепта',
    )
    image = models.ImageField(
        upload_to='recipes/',
        verbose_name='Изображение блюда'
    )
    text = models.TextField(
        verbose_name='Описание рецепта',
        help_text='Добавьте описание рецепта',
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='IngredientRecipe',
        verbose_name='Ингредиенты',
    )
    tags = models.ManyToManyField(
        Tag,
        related_name='recipes',
        verbose_name='Теги',
    )
    cooking_time = models.PositiveIntegerField(
        validators=[MinValueValidator(1,
                    message='Минимальное время приготовления 1 минута')],
        verbose_name='Время приготовления в минутах',
        help_text='Укажите время приготовления в минутах',
    )
    pub_date = models.DateTimeField(
        auto_now_add=True, verbose_name='Дата публикации'
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('-id',)

    def __str__(self):
        return self.name


class IngredientRecipe(models.Model):
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.PROTECT,
        verbose_name='Ингредиент, используемый в рецепте',
    )
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, verbose_name='Рецепт'
    )
    amount = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1)],
        verbose_name='Количество ингредиента'
    )

    class Meta:
        constraints = [UniqueConstraint(fields=['ingredient', 'recipe'],
                       name='unique_ingredient_in_recipe')]
        verbose_name = 'Ингридиент'
        verbose_name_plural = 'Ингридиенты'


class RecipeTag(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE,
                            verbose_name='Тег')

    class Meta:
        constraints = [UniqueConstraint(fields=['tag', 'recipe'],
                       name='unique_recipe_tag')]
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return 'Тег рецепта'


class Favorite(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorite',
        verbose_name='Пользователь',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorited_by',
        verbose_name='Рецепт',
    )

    class Meta:
        constraints = [models.UniqueConstraint(fields=['user', 'recipe'],
                       name='unique_recipe_in_user_favorite')]
        ordering = ('-id',)
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='shopping_cart',
        verbose_name='Пользователь',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт в списке покупок',
    )

    class Meta:
        constraints = [UniqueConstraint(fields=['user', 'recipe'],
                       name='unique_recipe_in_user_shopping_cart')]
        ordering = ('-id',)
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'
