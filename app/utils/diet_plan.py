import requests
import os
from dotenv import load_dotenv

load_dotenv()

SPOONACULAR_API_KEY = os.getenv("SPOONACULAR_API_KEY")

def get_spoonacular_meals(meal_type, diet=None, allergies=None, max_calories=None, number=1):
    """
    Fetches meals from Spoonacular API based on diet, allergies, and calorie limit.
    """
    url = "https://api.spoonacular.com/recipes/complexSearch"

    params = {
        "apiKey": SPOONACULAR_API_KEY,
        "type": meal_type,  # breakfast, lunch, dinner, snack
        "diet": diet,  # e.g., "vegetarian", "keto"
        "intolerances": ",".join(allergies) if allergies else None,
        "maxCalories": max_calories,
        "number": number,
        "addRecipeNutrition": True
    }

    try:
        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            return data.get("results", [])
        else:
            print("Spoonacular API Error:", response.status_code, response.text)
            return []
    except Exception as e:
        print(f"Error fetching from Spoonacular: {e}")
        return []


def generate_diet_plan(diet_type, allergies, calorie_target):
    """
    Returns a personalized daily meal plan dictionary with meal types as keys
    and recipe data as values.
    """
    plan = {}
    meal_plan_split = {
        "breakfast": 0.25,
        "lunch": 0.35,
        "snack": 0.10,
        "dinner": 0.30
    }

    for meal_type, portion in meal_plan_split.items():
        max_calories = int(calorie_target * portion)
        recipes = get_spoonacular_meals(
            meal_type=meal_type,
            diet=diet_type,
            allergies=allergies,
            max_calories=max_calories,
            number=1
        )
        if recipes:
            plan[meal_type] = recipes[0]
        else:
            plan[meal_type] = None

    return plan
