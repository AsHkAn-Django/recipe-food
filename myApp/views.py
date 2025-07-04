from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404, redirect, render
from django.views import generic
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.http import JsonResponse
from django.conf import settings

from .models import Recipe, Rating, RecipeIngredient
from .forms import IngredientForm, RecipeForm, RatingForm, RecipeIngredientFormSet, FilterRecipeForm
from .utils import ingredients_hash

import requests



URL = "https://trackapi.nutritionix.com/v2/natural/nutrients"


class IndexView(generic.ListView):
    model = Recipe
    context_object_name = 'recipes'
    template_name = "myApp/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        form = FilterRecipeForm(self.request.GET)
        context['form'] = form

        recipes = Recipe.objects.all()

        if form.is_valid():
            calories = form.cleaned_data.get('calories')
            if calories is not None:
                recipes = recipes.filter(calories__lte=calories)

            protein = form.cleaned_data.get('protein')
            if protein is not None:
                recipes = recipes.filter(protein__lte=protein)

            fat = form.cleaned_data.get('fat')
            if fat is not None:
                recipes = recipes.filter(fat__lte=fat)

            carbs = form.cleaned_data.get('carbs')
            if carbs is not None:
                recipes = recipes.filter(carbs__lte=carbs)

        context['recipes'] = recipes
        return context



class RecipeDetailView(generic.DetailView):
    model = Recipe
    template_name = "myApp/recipe_detail.html"
    context_object_name = 'recipe'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        recipe = context['recipe']
        fetch_nutrition(recipe)
        return context



def add_recipe(request):
    # We use or None instead of if reques is post else
    # We always give a formset an empty queryset for adding a new parent and not editing
    # We use prefix to avoid name collisions when multiple forms are in one page.
    recipe_form = RecipeForm(request.POST or None, request.FILES or None, prefix='recipe')
    formset = RecipeIngredientFormSet(request.POST or None, prefix='ingredients', queryset=RecipeIngredient.objects.none())
    ingredient_form = IngredientForm(request.POST or None, request.FILES or None, prefix='new_ing')

    # AJAX handler: add ingredient inline without losing form data
    if request.method == 'POST' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        if ingredient_form.is_valid():
            ing = ingredient_form.save()
            return JsonResponse({'success': True, 'id': ing.id, 'title': ing.title})
        return JsonResponse({'success': False, 'errors': ingredient_form.errors}, status=400)

    if request.method == 'POST':
        # 'submit_recipe' is the name of the button for submit so we realize user submited
        if 'submit_recipe' in request.POST:
            if recipe_form.is_valid() and formset.is_valid():
                recipe = recipe_form.save()
                instances = formset.save(commit=False)
                for idx, inst in enumerate(instances):
                    inst.recipe = recipe
                    inst.order = idx + 1  # auto-order
                    inst.save()

                # fetch nutrition and add it to recipe
                fetch_nutrition(recipe)

                messages.success(request, 'Recipe saved successfully!')
                return redirect('myApp:home')

    return render(request, 'myApp/add_recipe.html',
                  {'recipe_form': recipe_form,'formset': formset,'ingredient_form': ingredient_form})


def fetch_nutrition(recipe):
    """ Get hash, if recipe doesn't have nutrition or has been edited,
        fetch it again and add it to the recipe.
    """
    # Create the string ingredients and units
    ingredients_text = ", ".join(str(ing) for ing in recipe.recipe_ingredients.all())

    # Create a hash for it
    current_hash = ingredients_hash(ingredients_text)

    if not recipe.nutrition_hash or recipe.nutrition_hash != current_hash:
        headers = {
            "x-app-id": settings.NUTRITIONIX_APP_ID,
            "x-app-key": settings.NUTRITIONIX_APP_KEY,
            "Content-Type": "application/json"
        }

        data = {
            "query": ingredients_text,
            "timezone": "US/Eastern"
        }

        try:
            response = requests.post(URL, headers=headers, json=data)
            response.raise_for_status()
            print(f'The Fetched Data: {response.json()}')

            recipe.nutrition_data = response.json()
            recipe.nutrition_hash = current_hash
            recipe.save()
            calculate_nutrition_fields(recipe)

            print('DATA HAS BEEN FETCHED AND SAVED')

        except requests.RequestException as e:
            print(f"Nutrition API error: {e}")

    elif not recipe.calories:
        calculate_nutrition_fields(recipe)


def calculate_nutrition_fields(recipe):
    calories = 0.0
    protein = 0.0
    fat = 0.0
    carbs = 0.0
    for food in recipe.nutrition_data.get("foods", []):
        calories += food.get("nf_calories", 0)
        protein += food.get("nf_protein", 0)
        fat += food.get("nf_total_fat", 0)
        carbs += food.get("nf_total_carbohydrate", 0)

    recipe.calories = round(calories, 2)
    recipe.protein = round(protein, 2)
    recipe.fat = round(fat, 2)
    recipe.carbs = round(carbs, 2)
    print('✅ NUTRITION FIELDS FILLED ✅')
    recipe.save()


class FilterListView(generic.ListView):
    template_name = "myApp/filter_list.html"
    context_object_name = 'recipes'

    def get_queryset(self):
        query = self.request.GET.get('query')
        if query:
            return Recipe.objects.filter(Q(title__icontains=query) |
                                         Q(instruction__icontains=query) |
                                         Q(ingredients__title__icontains=query)).distinct()
        return Recipe.objects.none()


class RatingFormView(LoginRequiredMixin, generic.FormView):
    model = Rating
    form_class = RatingForm
    success_url = reverse_lazy('myApp:home')
    template_name = "myApp/rating_form.html"

    def form_valid(self, form):
        recipe_id = self.kwargs.get('pk')
        rate_exist = Rating.objects.filter(recipe_id=recipe_id, user=self.request.user)
        if rate_exist:
            rate_exist.delete()
        form.instance.user = self.request.user
        form.instance.recipe = get_object_or_404(Recipe, id=recipe_id)
        form.save()
        messages.success(self.request, 'You have rated the recipe successfully.')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        recipe_id = self.kwargs.get('pk')
        context['recipe'] = get_object_or_404(Recipe, id=recipe_id)
        return context