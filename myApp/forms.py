from django import forms
from .models import Ingredient, Recipe, Rating, RecipeIngredient
from django.forms import inlineformset_factory
from django.forms.models import BaseInlineFormSet



class FilterRecipeForm(forms.Form):
    calories = forms.DecimalField(
        min_value=0, max_value=10000, decimal_places=2, max_digits=8,
        required=False, label='Calories less than:',
        widget=forms.TextInput(attrs={'placeholder': 'Ex. 50.4'})
    )
    protein = forms.DecimalField(
        min_value=0, max_value=1000, decimal_places=2, max_digits=8,
        required=False, label="Protein less than:",
        widget=forms.TextInput(attrs={'placeholder': 'Ex. 50.4'})
    )
    fat = forms.DecimalField(
        min_value=0, max_value=1000, decimal_places=2, max_digits=8,
        required=False, label="Fat less than:",
        widget=forms.TextInput(attrs={'placeholder': 'Ex. 50.4'})
    )
    carbs = forms.DecimalField(
        min_value=0, max_value=1000, decimal_places=2, max_digits=8,
        required=False, label='Carbs less than:',
        widget=forms.TextInput(attrs={'placeholder': 'Ex. 50.4'})
    )


class RecipeIngredientBaseFormSet(BaseInlineFormSet):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for form in self.forms:
            form.empty_permitted = True


class IngredientForm(forms.ModelForm):

    class Meta:
        model = Ingredient
        fields = ['title', 'picture']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'picture': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }


class RecipeForm(forms.ModelForm):

    class Meta:
        model = Recipe
        fields = ['title', 'instruction', 'picture']


class RecipeIngredientForm(forms.ModelForm):

    class Meta:
        model = RecipeIngredient
        fields = ['ingredient', 'quantity', 'unit', 'order']
        widgets = {
            'ingredient': forms.Select(attrs={'class': 'form-select'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control'}),
            'unit': forms.TextInput(attrs={'class': 'form-control'}),
        }


RecipeIngredientFormSet = inlineformset_factory(
    Recipe,
    RecipeIngredient,
    form=RecipeIngredientForm,
    formset=RecipeIngredientBaseFormSet,
    fields=['ingredient', 'quantity', 'unit'],
    extra=1,
    can_delete=True,
)


class RatingForm(forms.ModelForm):

    class Meta:
        model = Rating
        fields = ['rate']
        labels = {
            'rate': 'Rate between 1-5'
        }