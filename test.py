from app import app
from fastapi.testclient import TestClient

client = TestClient(app)


def test_get_all_recipes():
    """
    Тестирование получения списка всех рецептов.

    Проверяет:
        - Код ответа 200 OK
        - Тело ответа - непустой список
        - Каждый рецепт содержит обязательные поля:
            * title (название)
            * cooking_time (время приготовления)
            * views (количество просмотров)
    """
    response = client.get("/recipes/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    for recipe in data:
        assert "title" in recipe
        assert "cooking_time" in recipe
        assert "views" in recipe


def test_get_recipe_by_id():
    """
    Тестирование получения конкретного рецепта по ID.

    Проверяет:
        - Код ответа 200 OK
        - Тело ответа содержит полную информацию о рецепте:
            * title (название)
            * cooking_time (время приготовления)
            * description (описание)
            * list_of_ingredients (список ингредиентов)
    """
    response = client.get("/recipes/1")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "title" in data
    assert "cooking_time" in data
    assert "description" in data
    assert "list_of_ingredients" in data


def test_get_recipe_by_invalid_id():
    """
    Тестирование обработки запроса несуществующего рецепта.

    Проверяет:
        - Код ответа 404 Not Found
        - Наличие сообщения об ошибке в формате:
            {"error": "No recipe with this id"}
    """
    response = client.get("/recipes/99999")
    assert response.status_code == 404
    data = response.json()
    assert "error" in data
    assert data["error"] == "No recipe with this id"


def test_add_new_recipe():
    """
    Тестирование добавления нового рецепта.

    Проверяет:
        - Код ответа 201 Created
        - Сохранение всех переданных данных:
            * title
            * cooking_time
            * description
            * list_of_ingredients
        - Корректность сохраненного списка ингредиентов
    """
    new_recipe = {
        "title": "New Test Recipe",
        "cooking_time": 15,
        "description": "This is a new test recipe.",
        "list_of_ingredients": ["ingredient1", "ingredient2"],
    }

    response = client.post("/recipes/", json=new_recipe)
    assert response.status_code == 201
    data = response.json()
    assert "title" in data
    assert data["title"] == "New Test Recipe"
    assert "cooking_time" in data
    assert data["cooking_time"] == 15
    assert "description" in data
    assert data["description"] == "This is a new test recipe."
    assert "list_of_ingredients" in data
    assert len(data["list_of_ingredients"]) == 2


def test_add_duplicate_recipe():
    """
    Тестирование попытки добавления дубликата рецепта.

    Проверяет:
        - Код ответа 409 Conflict
        - Наличие сообщения об ошибке в формате:
            {"error": "Recipe already exists"}
    """
    duplicate_recipe = {
        "title": "New Test Recipe",
        "cooking_time": 15,
        "description": "This is a duplicate test recipe.",
        "list_of_ingredients": ["ingredient1", "ingredient2"],
    }

    response = client.post("/recipes/", json=duplicate_recipe)
    assert response.status_code == 409
    data = response.json()
    assert "error" in data
    assert data["error"] == "Recipe already exists"
