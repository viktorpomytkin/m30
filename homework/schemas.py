from typing import List

from pydantic import BaseModel, Field


class BaseRecipe(BaseModel):
    """
    Базовый класс для моделей рецептов, содержащий общие поля.

    Attributes:
        title: Название блюда
        cooking_time: Время приготовления в минутах (≥1)
    """

    title: str = Field(description="Name of this dish.")
    cooking_time: int = Field(ge=1, description="Time to cook this meal in minutes.")


class RecipeIn(BaseRecipe):
    """
    Модель для создания/обновления рецепта (входные данные API).

    Attributes:
        views: Количество просмотров (только для внутреннего использования)
        list_of_ingredients: Список ингредиентов блюда
        description: Описание блюда
    """

    views: int = Field(
        description="Not a necessary parameter. Initially always 0.",
        default=0,
        ge=0,
        le=0,
    )
    list_of_ingredients: List[str] = Field(
        description="List of str: ingredients that are included in the dish."
    )
    description: str = Field(description="Description of the dish.")


class RecipeOutShort(BaseRecipe):
    """
    Модель для краткого отображения рецепта.

    Attributes:
        views: Количество просмотров рецепта
    """

    views: int = Field(description="How many times this recipe was viewed.")


class RecipeOutLong(BaseRecipe):
    """
    Модель для полного отображения рецепта.

    Attributes:
        list_of_ingredients: Список ингредиентов блюда
        description: Описание блюда
    """

    list_of_ingredients: List[str] = Field(
        description="List of str: ingredients that are included in the dish."
    )
    description: str = Field(description="Description of the dish.")
