from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from django.contrib.auth.models import User
from decimal import Decimal


class Ingredient(models.Model):
    title = models.CharField(max_length=264, unique=True)
    picture = models.ImageField(upload_to='images/')

    def __str__(self):
        return self.title


class Recipe(models.Model):
    title = models.CharField(max_length=264)
    instruction = models.CharField(max_length=264)
    picture = models.ImageField(upload_to='images/')
    ingredients = models.ManyToManyField(Ingredient, related_name='recipes', through='RecipeIngredient')
    nutrittion_data = models.JSONField(null=True, blank=True)
    nutrition_hash = models.CharField(max_length=64, blank=True, null=True)

    def get_average_rating(self):
        ratings = self.ratings.all()
        if not ratings:
            return Decimal('0.0')
        else:
            total = sum(rating.rate for rating in ratings)
        return Decimal(round(total / len(ratings), 1))

    # TODO: Or a better wayyyyy:
    # from django.db.models import Avg
    # from decimal import Decimal
    # def get_average_rating(self):
    #     avg_rating = self.ratings.aggregate(avg=Avg("rate"))["avg"]
    #     return Decimal(round(avg_rating, 1)) if avg_rating is not None else Decimal("0.0")

    def __str__(self):
        return self.title


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='recipe_ingredents')
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE, related_name='ingredients')
    quantity = models.DecimalField(max_digits=6, decimal_places=1)
    unit = models.CharField(max_length=100)
    order = models.PositiveIntegerField()

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['recipe', 'ingredient'], name='unique_recipe_ingredient')
        ]
        ordering = ['order']

    def __str__(self):
        return f'{self.amount} of {self.ingredient.title}'


class Rating(models.Model):
    rate = models.DecimalField(max_digits=2, decimal_places=1, validators=[MaxValueValidator(5.0), MinValueValidator(1.0)])
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='ratings')
    date = models.DateTimeField(auto_now=True)
    review = models.CharField(max_length=250, null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} rateed {self.rate} to {self.recipe.title}"
