from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404, redirect, render
from django.views import generic
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.http import JsonResponse

from .models import Recipe, Rating, RecipeIngredient
from .forms import IngredientForm, RecipeForm, RatingForm, RecipeIngredientFormSet



class IndexView(generic.ListView):
    model = Recipe
    context_object_name = 'recipes'
    template_name = "myApp/index.html"


class RecipeDetailView(generic.DetailView):
    model = Recipe
    template_name = "myApp/recipe_detail.html"
    context_object_name = 'recipe'


def add_recipe(request):
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
        # Recipe + ingredients submission
        if 'submit_recipe' in request.POST:
            if recipe_form.is_valid() and formset.is_valid():
                recipe = recipe_form.save()
                instances = formset.save(commit=False)
                for idx, inst in enumerate(instances):
                    inst.recipe = recipe
                    inst.order = idx + 1  # auto-order
                    inst.save()
                messages.success(request, 'Recipe saved successfully!')
                return redirect('myApp:home')
        # fall through to render errors

    return render(request, 'myApp/add_recipe.html', {
        'recipe_form': recipe_form,
        'formset': formset,
        'ingredient_form': ingredient_form,
    })


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