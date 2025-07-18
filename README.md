# Recipe-Food With Nutritions Table

Just a simple recipe book web app I built while practicing Django and backend development. I’m sharing it here as part of my learning journey—every project helps me improve a bit more.

## About the Project

This app lets users add recipes and get automatic nutritional information based on the ingredients. It uses the [Nutritionix API](https://developer.nutritionix.com/) to fetch details like calories, protein, fat, and carbs. It also includes search and filter functionality so users can browse recipes based on nutritional values.

The goal was to learn how to work with external APIs, improve form handling in Django, and cleanly manage model relationships like recipes and ingredients. I also spent time making sure the UI stays simple and usable.

## Features

- Add recipes with multiple ingredients
- Automatically fetch calorie, protein, fat, and carb data from the Nutritionix API
- Search and filter recipes by nutritional criteria (calories, protein, fat, carbs)
- Inline ingredient creation with AJAX
- User ratings for recipes
- Simple and clean Bootstrap-based layout

## Tech Stack

- **Backend:** Django (Python)
- **Frontend:** HTML, CSS, Bootstrap
- **Database:** SQLite (default Django setup)
- **Other:** Nutritionix API, JavaScript (for AJAX in forms)

## Setup Instructions

If you want to try it out locally:

```bash
git clone https://github.com/AsHkAn-Django/recipe-food.git
cd recipe-food
python -m venv .venv
source .venv/bin/activate   # or .venv\Scripts\activate on Windows
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

After running the server, open your browser at \`http://127.0.0.1:8000/\`.

## Notes

- To use the Nutritionix API, you’ll need to get your own API keys and add them to your `.env` or `settings.py` file:
```python
  NUTRITIONIX_APP_ID = 'your_app_id'
  NUTRITIONIX_APP_KEY = 'your_app_key'
```
- The nutrition data only updates if the recipe is new or the ingredient list changes (controlled with a hash check).
- The search function works for recipe titles, instructions, and ingredient names.

## Why I Made This

I wanted to learn how to integrate third-party APIs into Django projects and work with nested formsets. I also wanted to practice building something that feels more real and useful. The idea came from thinking about how people often want to know the nutrition info of what they’re cooking—but don’t want to do the math manually.

## About Me

Hey, I’m Ashkan. I used to teach English, but I’ve recently made the switch to web development—specifically backend development with Django. Right now I’m focused on learning, building projects, and eventually finding remote work as a junior developer.

- [GitHub](https://github.com/AsHkAn-Django)
- [LinkedIn](https://www.linkedin.com/in/ashkan-ahrari-146080150)

