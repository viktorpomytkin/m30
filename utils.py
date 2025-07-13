from typing import Iterable, List, Optional, Sequence, Set

from sqlalchemy.future import select

from database import session
from models import Ingredient, Recipe, RecipeIngredient


async def increase_view_count(recipe_id: Optional[int] = None) -> None:
    """
    Увеличивает счетчик просмотров для одного или всех рецептов.

    Args:
        recipe_id (Optional[int]): ID рецепта, для которого нужно увеличить счетчик просмотров.
            Если не указан, счетчик увеличивается для всех рецептов.

    Returns:
        None

    Notes:
        - Если передан recipe_id: увеличивает счетчик только для указанного рецепта
        - Если recipe_id не передан: увеличивает счетчики для всех рецептов
        - Использует модель Recipe
    """
    if recipe_id:
        recipe_selection = await session.execute(
            select(Recipe).filter(Recipe.id == recipe_id)
        )
        recipe: Recipe = recipe_selection.scalars().one()
        recipe.views += 1
        session.add(recipe)
    else:
        recipe_selection = await session.execute(select(Recipe))
        recipes: Sequence[Recipe] = recipe_selection.scalars().all()
        for recipe in recipes:
            recipe.views += 1
        session.add_all(recipes)

    await session.commit()


async def add_ingredients(current_ingredients: Set[str]) -> None:
    """
    Добавляет новые ингредиенты в базу данных.

    Args:
        current_ingredients (Set[str]): Множество названий ингредиентов для добавления

    Returns:
        None

    Notes:
        - Проверяет существующие ингредиенты в базе
        - Добавляет только новые ингредиенты
        - Использует модель Ingredient
    """
    ingredients_in_db = await session.execute(
        select(Ingredient).filter(Ingredient.name.in_(current_ingredients))
    )
    ingredients_in_db = [
        ingredient.name for ingredient in ingredients_in_db.scalars().all()
    ]
    new_ingredients_set: Set[str] = (
        current_ingredients - set(ingredients_in_db)
        if ingredients_in_db
        else current_ingredients
    )
    new_ingredients_list: List[Ingredient] = [
        Ingredient(name=new_ingredient) for new_ingredient in new_ingredients_set
    ]
    session.add_all(new_ingredients_list)


async def add_recipe_ingredients(
    ingredients_ids: Iterable[int], recipe_id: int
) -> None:
    """
    Связывает ингредиенты с рецептом через промежуточную таблицу.

    Args:
        ingredients_ids (Iterable[int]): Коллекция ID ингредиентов
        recipe_id (int): ID рецепта, с которым нужно связать ингредиенты

    Returns:
        None

    Notes:
        - Создает связи в таблице RecipeIngredient
        - Использует модель RecipeIngredient
    """
    recipe_ingredients_list: List[RecipeIngredient] = [
        RecipeIngredient(recipe_id=recipe_id, ingredient_id=ingredient_id)
        for ingredient_id in ingredients_ids
    ]

    session.add_all(recipe_ingredients_list)


async def get_ingredients_list(recipe_id: int) -> List[str]:
    """
    Возвращает список названий ингредиентов для указанного рецепта.

    Args:
        recipe_id (int): ID рецепта, для которого нужно получить ингредиенты

    Returns:
        List[str]: Список названий ингредиентов

    Notes:
        - Получает связи из таблицы RecipeIngredient
        - Возвращает названия ингредиентов из таблицы Ingredient
        - Использует модели RecipeIngredient и Ingredient
    """
    ingredients_ids_res = await session.execute(
        select(RecipeIngredient).filter(RecipeIngredient.recipe_id == recipe_id)
    )
    ingredients_ids: List[int] = [
        ingredient.ingredient_id for ingredient in ingredients_ids_res.scalars().all()
    ]

    ingredients_res = await session.execute(
        select(Ingredient).filter(Ingredient.id.in_(ingredients_ids))
    )
    ingredients: List[str] = [
        ingredient.name for ingredient in ingredients_res.scalars().all()
    ]

    return ingredients
