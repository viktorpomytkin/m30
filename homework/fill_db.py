from sqlalchemy.future import select

from database import session
from models import Ingredient, Recipe, RecipeIngredient


async def populate_db():
    recipes_in_db_res = await session.execute(select(Recipe))

    if not recipes_in_db_res.scalars().all():
        recipes_data = [
            {
                "title": "Spaghetti Carbonara",
                "description": "A classic Italian pasta dish made with "
                               "eggs, cheese, pancetta, and pepper.",
                "cooking_time": 20,
                "views": 0,
            },
            {
                "title": "Chicken Curry",
                "description": "A flavorful chicken curry made with a blend"
                               " of spices, tomatoes, and coconut milk.",
                "cooking_time": 40,
                "views": 0,
            },
            {
                "title": "Beef Stroganoff",
                "description": "A Russian dish of sautéed pieces "
                               "of beef served in a sauce with sour cream.",
                "cooking_time": 30,
                "views": 0,
            },
            {
                "title": "Vegetable Stir Fry",
                "description": "A quick and healthy stir fry with "
                               "a mix of fresh vegetables and soy sauce.",
                "cooking_time": 15,
                "views": 0,
            },
            {
                "title": "Pancakes",
                "description": "Fluffy pancakes made with flour, milk,"
                               " eggs, and butter, served with syrup.",
                "cooking_time": 10,
                "views": 0,
            },
        ]

        ingredients_data = [
            {"name": "Eggs"},
            {"name": "Cheese"},
            {"name": "Pancetta"},
            {"name": "Pepper"},
            {"name": "Chicken"},
            {"name": "Curry Powder"},
            {"name": "Tomatoes"},
            {"name": "Coconut Milk"},
            {"name": "Beef"},
            {"name": "Sour Cream"},
            {"name": "Vegetables"},
            {"name": "Soy Sauce"},
            {"name": "Flour"},
            {"name": "Milk"},
            {"name": "Butter"},
            {"name": "Syrup"},
        ]

        recipe_ingredient_data = [
            {"recipe_id": 1, "ingredient_id": 1},  # Spaghetti Carbonara - Eggs
            {"recipe_id": 1, "ingredient_id": 2},  # Spaghetti Carbonara-Cheese
            {"recipe_id": 1, "ingredient_id": 3},  # Spaghetti Carbonara-Pancet
            {"recipe_id": 1, "ingredient_id": 4},  # Spaghetti Carbonara - Pepp
            {"recipe_id": 2, "ingredient_id": 5},  # Chicken Curry - Chicken
            {"recipe_id": 2, "ingredient_id": 6},  # Chicken Curry - Curry Powd
            {"recipe_id": 2, "ingredient_id": 7},  # Chicken Curry - Tomatoes
            {"recipe_id": 2, "ingredient_id": 8},  # Chicken Curry - Coconut Mi
            {"recipe_id": 3, "ingredient_id": 9},  # Beef Stroganoff - Beef
            {"recipe_id": 3, "ingredient_id": 10},  # Beef Stroganoff - Sour Cr
            {"recipe_id": 4, "ingredient_id": 11},  # Vegetable Stir Fry-Vegeta
            {"recipe_id": 4, "ingredient_id": 12},  # Vegetable Stir Fry-SoySau
            {"recipe_id": 5, "ingredient_id": 13},  # Pancakes - Flour
            {"recipe_id": 5, "ingredient_id": 14},  # Pancakes - Milk
            {"recipe_id": 5, "ingredient_id": 15},  # Pancakes - Butter
            {"recipe_id": 5, "ingredient_id": 16},  # Pancakes - Syrup
        ]

        recipes = [Recipe(**recipe) for recipe in recipes_data]
        ingredients = [Ingredient(**ingredient) for ingredient in ingredients_data]
        recipe_ingredient = [
            RecipeIngredient(**recipe_ingredient)
            for recipe_ingredient in recipe_ingredient_data
        ]

        session.add_all(recipes)
        session.add_all(ingredients)
        session.add_all(recipe_ingredient)

        await session.commit()
