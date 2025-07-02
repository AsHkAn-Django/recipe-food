from django.contrib import admin
from .models import Recipe, Ingredient, Rating, RecipeIngredient


admin.site.register(Recipe)
admin.site.register(Ingredient)
admin.site.register(Rating)
admin.site.register(RecipeIngredient)