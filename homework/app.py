from typing import Annotated, Any, Dict, List, Sequence, Set, Union

import schemas
from database import engine, session
from fastapi import FastAPI, Path, Response, status
from fill_db import populate_db
from models import Base, Ingredient, Recipe
from sqlalchemy import desc
from sqlalchemy.future import select
from utils import (add_ingredients, add_recipe_ingredients,
                   get_ingredients_list, increase_view_count)

app = FastAPI()


@app.on_event("startup")
async def startup():
    """
    Инициализирует базу данных при запуске сервера.

    Действия:
        - Создаёт все таблицы (Base.metadata.create_all).
        - Заполняет БД тестовыми данными (populate_db()).
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        await populate_db()


@app.on_event("shutdown")
async def shutdown():
    """
    Корректно закрывает соединения с БД при остановке сервера.

    Действия:
        - Закрывает сессию (session.close()).
        - Освобождает ресурсы подключения (engine.dispose()).
    """
    await session.close()
    await engine.dispose()


@app.get("/recipes/", response_model=List[schemas.RecipeOutShort])
async def get_all_recipes() -> Sequence[Recipe]:
    """
    Возвращает список всех рецептов,
    отсортированных по популярности и времени приготовления.

    Returns:
        Sequence[Recipe]: Список рецептов в формате:
            [
                {
                    "id": int,
                    "title": str,
                    "cooking_time": int,
                    "views": int
                },
                ...
            ]
    """
    res = await session.execute(
        select(Recipe).order_by(desc(Recipe.views), Recipe.cooking_time)
    )
    return res.scalars().all()


@app.get("/recipes/{recipe_id}", response_model=Union[schemas.RecipeOutLong, Dict])
async def get_recipe_by_id(
    recipe_id: Annotated[int, Path(title="Id of a recipe", ge=1)], response: Response
) -> Dict[str, Any]:
    """
    Возвращает полную информацию о рецепте по его ID.
    Увеличивает счётчик просмотров.

    Args:
        recipe_id (int, Path): ID рецепта (≥ 1).
        response (Response): Объект ответа FastAPI для установки статуса.

    Returns:
        Dict[str, Any]: Рецепт в формате:
            {
                "title": str,
                "cooking_time": int,
                "description": str,
                "list_of_ingredients": List[str]
            }
        или {"error": str}, если рецепт не найден.

    Raises:
        HTTP 404: Если рецепт не существует.
    """
    res = await session.execute(select(Recipe).filter(Recipe.id == recipe_id))
    output: Recipe = res.scalars().one_or_none()
    if output:
        output: Dict[str, Any] = output.to_dict()
        output.pop("views")
        recipe_id: int = output.pop("id")
        list_of_ingredients: List[str] = await get_ingredients_list(recipe_id)
        output.update(list_of_ingredients=list_of_ingredients)
        await increase_view_count(recipe_id)
        return output
    else:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"error": "No recipe with this id"}


@app.post(
    "/recipes/", response_model=Union[schemas.RecipeOutLong, Dict], status_code=201
)
async def add_new_recipe(
    recipe: schemas.RecipeIn, response: Response
) -> Dict[str, Any]:
    """
    Добавляет новый рецепт в базу данных.

    Args:
        recipe (schemas.RecipeIn): Данные рецепта в формате:
            {
                "title": str,
                "cooking_time": int,
                "description": str,
                "list_of_ingredients": List[str]
            }
        response (Response): Объект ответа FastAPI для установки статуса.

    Returns:
        Dict[str, Any]: Созданный рецепт (аналогично GET /recipes/{id}).
        или {"error": str}, если рецепт уже существует.

    Raises:
        HTTP 409: Если рецепт с таким названием уже есть.
    """
    res = await session.execute(select(Recipe).filter(Recipe.title == recipe.title))
    res = res.scalars().all()
    if not res:
        recipe: Dict[str, Union[str, int, List[str]]] = recipe.dict()
        ingredients: Set[str] = set(recipe.pop("list_of_ingredients"))
        new_recipe = Recipe(**recipe)
        session.add(new_recipe)
        await add_ingredients(ingredients)

        await session.commit()

        ingredients_with_ids = (
            (
                await session.execute(
                    select(Ingredient).filter(Ingredient.name.in_(ingredients))
                )
            )
            .scalars()
            .all()
        )
        ingredients_ids: List[int] = [
            ingredient.id for ingredient in ingredients_with_ids
        ]

        new_recipe = await session.execute(
            select(Recipe).filter(Recipe.title == recipe.get("title"))
        )
        output: Dict[str, Any] = new_recipe.scalars().one().to_dict()
        output.pop("views")
        new_recipe_id: int = output.pop("id")
        await add_recipe_ingredients(ingredients_ids, new_recipe_id)

        await session.commit()
        list_of_ingredients: List[str] = await get_ingredients_list(new_recipe_id)
        output.update(list_of_ingredients=list_of_ingredients)
        return output
    else:
        response.status_code = status.HTTP_409_CONFLICT
        return {"error": "Recipe already exists"}
