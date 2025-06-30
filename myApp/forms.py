from django import forms
from .models import Ingredient, Recipe, Rating


class IngredientForm(forms.ModelForm):
    class Meta:
        model = Ingredient
        fields = "__all__"


class RecipeForm(forms.ModelForm):
    class Meta:
        model = Recipe
        fields = "__all__"
        

class RatingForm(forms.ModelForm):
    class Meta:
        model = Rating
        fields = ['rate']
        labels = {
            'rate': 'Rate between 1-5'
        }