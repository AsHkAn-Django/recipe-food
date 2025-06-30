from django.contrib import admin
from .models import Recipe, Ingredient, Rating


admin.site.register(Recipe)
admin.site.register(Ingredient)
admin.site.register(Rating)