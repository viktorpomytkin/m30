from typing import Any, Dict

from database import Base
from sqlalchemy import Column, ForeignKey, Integer, Text
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm import relationship


class Recipe(Base):
    """
    Модель представляет рецепт в системе.

    Атрибуты:
        id (int): Уникальный идентификатор рецепта (PK, автоинкремент)
        title (str): Название рецепта (обязательное)
        description (str): Описание рецепта (необязательное)
        cooking_time (int): Время приготовления в минутах (обязательное)
        views (int): Количество просмотров (по умолчанию 0)

    Отношения:
        recipe_ingredient: Связь с ассоциативной таблицей RecipeIngredient
        ingredients: Прокси для доступа к ингредиентам
    """

    __tablename__ = "recipes"
    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    title = Column(Text, index=True, nullable=False)
    description = Column(Text, index=True, nullable=True)
    cooking_time = Column(Integer, index=True, nullable=False)
    views = Column(Integer, default=0)

    recipe_ingredient = relationship(
        "RecipeIngredient", back_populates="recipes", cascade="all"
    )
    ingredients = association_proxy("recipe_ingredient", "ingredients")

    def to_dict(self) -> Dict[str, Any]:
        """
        Преобразует объект рецепта в словарь.

        Returns:
            Dict[str, Any]: Словарь с ключами id, title, description,
            cooking_time, views
        """
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "cooking_time": self.cooking_time,
            "views": self.views,
        }


class Ingredient(Base):
    """
    Модель представляет ингредиент, используемый в рецептах.

    Атрибуты:
        id (int): Уникальный идентификатор ингредиента (PK, автоинкремент)
        name (str): Название ингредиента (уникальное)

    Отношения:
        recipe_ingredient: Связь с ассоциативной таблицей RecipeIngredient
        recipes: Прокси для доступа к рецептам
    """

    __tablename__ = "ingredients"
    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    name = Column(Text, unique=True, index=True)

    recipe_ingredient = relationship(
        "RecipeIngredient", back_populates="ingredients", cascade="all"
    )
    recipes = association_proxy("recipe_ingredient", "recipes")


class RecipeIngredient(Base):
    """
    Ассоциативная таблица для связи многие-ко-многим между рецептами и ингредиентами.

    Атрибуты:
        recipe_id (int): Внешний ключ на таблицу recipes (часть составного PK)
        ingredient_id (int): Внешний ключ на таблицу ingredients (часть составного PK)

    Отношения:
        recipes: Связь с моделью Recipe
        ingredients: Связь с моделью Ingredient
    """

    __tablename__ = "recipe_ingredient"
    recipe_id = Column(
        Integer, ForeignKey("recipes.id"), primary_key=True, nullable=False
    )
    ingredient_id = Column(
        Integer, ForeignKey("ingredients.id"), primary_key=True, nullable=False
    )

    recipes = relationship("Recipe", back_populates="recipe_ingredient")
    ingredients = relationship("Ingredient", back_populates="recipe_ingredient")
