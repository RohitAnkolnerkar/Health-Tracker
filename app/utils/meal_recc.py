import requests
import os
from dotenv import load_dotenv

load_dotenv()

SPOONACULAR_API_KEY = os.getenv("SPOONACULAR_API_KEY")

def get_spoonacular_meals(meal_type, diet=None, allergies=None, max_calories=None, number=5):
    url = "https://api.spoonacular.com/recipes/complexSearch"

    params = {
        "apiKey": SPOONACULAR_API_KEY,
        "type": meal_type,
        "diet": diet,  # e.g., "vegetarian", "keto"
        "intolerances": ",".join(allergies) if allergies else None,
        "maxCalories": max_calories,
        "number": number,
        "addRecipeNutrition": True
    }

    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        return data.get("results", [])
    else:
        print("Error:", response.status_code, response.text)
        return []
