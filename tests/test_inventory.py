import pytest
from fastapi import HTTPException
from sqlalchemy.orm import Session

from inventory import schemas, crud, models
from users.auth import create_access_token


# Category tests
def test_create_category(db_session):
    category_data = schemas.CategoryCreate(name="Electronics")
    category = crud.create_category(db=db_session, category=category_data)
    assert category.name == "Electronics"


def test_create_category_duplicate(db_session):
    category_data = schemas.CategoryCreate(name="Electronics")
    crud.create_category(db=db_session, category=category_data)

    with pytest.raises(HTTPException) as exc_info:
        crud.create_category(db=db_session, category=category_data)

    assert exc_info.value.status_code == 400
    assert "Category with this name already exists." in str(exc_info.value.detail)


def test_create_category_authorized(test_client, create_test_user):
    """Тестирование авторизованного создания категории с использованием токена"""

    token = create_access_token(data={"sub": str(create_test_user.id)})

    headers = {
        "Authorization": f"Bearer {token}"
    }

    category_data = {"name": "Electronics"}
    response = test_client.post("/categories/", json=category_data, headers=headers)

    assert response.status_code == 200
    assert response.json()["name"] == "Electronics"


def test_create_category_unauthorized(test_client):
    """Тестирование создания категории без авторизации"""

    category_data = {"name": "Electronics"}
    response = test_client.post("/categories/", json=category_data)
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"


def test_get_category_by_name(db_session):
    category_data = schemas.CategoryCreate(name="Electronics")
    crud.create_category(db=db_session, category=category_data)
    category = crud.get_category_by_name(db=db_session, name="Electronics")
    assert category is not None
    assert category.name == "Electronics"


def test_delete_category(db_session):
    category_data = schemas.CategoryCreate(name="Electronics")
    category = crud.create_category(db=db_session, category=category_data)
    deleted_category = crud.delete_category(db=db_session, category_id=category.id)
    assert deleted_category is not None
    assert deleted_category.name == "Electronics"


def test_delete_category_authorized(test_client, create_test_user, db_session):
    """Тестирование удаления категории с авторизацией"""

    token = create_access_token(data={"sub": str(create_test_user.id)})
    headers = {"Authorization": f"Bearer {token}"}

    category_data = {"name": "Electronics"}
    response = test_client.post("/categories/", json=category_data, headers=headers)
    assert response.status_code == 200
    created_category = response.json()

    response = test_client.delete(f"/categories/{created_category['id']}", headers=headers)
    assert response.status_code == 200
    deleted_category = response.json()
    assert deleted_category["name"] == "Electronics"


def test_delete_category_unauthorized(test_client, db_session):
    """Тестирование удаления категории без авторизации"""

    category_data = schemas.CategoryCreate(name="Electronics")
    category = crud.create_category(db=db_session, category=category_data)

    response = test_client.delete(f"/categories/{category.id}")

    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"


def test_get_all_categories_query(db_session):
    category1 = models.Category(name="Category 1")
    category2 = models.Category(name="Category 2")
    db_session.add_all([category1, category2])
    db_session.commit()

    result = crud.get_all_categories_query(db_session).all()

    assert len(result) == 2
    assert result[0].name == "Category 1"
    assert result[1].name == "Category 2"


# Item tests
def test_get_item_by_id(db_session: Session, create_test_item):
    """Test for getting an item by its ID."""
    result = crud.get_item_by_id(db_session, create_test_item.id)
    assert result.name == "Test Item"
    assert result.description == "Test Description"
    assert result.category == create_test_item.category

    with pytest.raises(HTTPException) as exc_info:
        crud.get_item_by_id(db_session, 999)
    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Item not found."


def test_get_item_by_name(db_session: Session, create_test_item):
    """Test for getting an item by its name."""
    result = crud.get_item_by_name(db_session, create_test_item.name)
    assert result is not None
    assert result.name == "Test Item"
    assert result.description == "Test Description"

    result = crud.get_item_by_name(db_session, "Nonexistent Item")
    assert result is None


def test_get_all_items_query(db_session: Session, create_test_user, create_test_category):
    """Test for getting all items."""

    item1 = models.Item(
        name="Test Item 1",
        description="Test Description 1",
        category=create_test_category.name,
        quantity=5,
        price=100.0,
        creator_id=create_test_user.id
    )

    item2 = models.Item(
        name="Test Item 2",
        description="Test Description 2",
        category=create_test_category.name,
        quantity=10,
        price=200.0,
        creator_id=create_test_user.id
    )

    db_session.add_all([item1, item2])
    db_session.commit()

    query = crud.get_all_items_query(db_session)
    items = query.all()
    assert len(items) == 2
    assert items[0].name == "Test Item 1"
    assert items[1].name == "Test Item 2"


def test_validate_category_exists_success(db_session: Session, create_test_category):
    """Test successful validation of an existing category."""
    try:
        crud.validate_category_exists(db_session, create_test_category.name)
    except HTTPException:
        pytest.fail("HTTPException raised unexpectedly for existing category")


def test_validate_category_exists_failure(db_session: Session):
    """Test validation failure for non-existing category."""
    with pytest.raises(HTTPException) as exc_info:
        crud.validate_category_exists(db_session, "Nonexistent Category")

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail["message"] == "This category does not exist! Create it first or choose an existing category."
    assert "existing_categories" in exc_info.value.detail


def test_create_item_success(db_session: Session, create_test_user, create_test_category):
    """Test successful item creation."""
    item_data = schemas.ItemCreate(
        name="Test Item",
        description="Test Description",
        category=create_test_category.name,
        quantity=10,
        price=200.0
    )

    item = crud.create_item(db_session, item_data, creator_id=create_test_user.id)
    assert item.name == "Test Item"
    assert item.description == "Test Description"
    assert item.category == create_test_category.name
    assert item.quantity == 10
    assert item.price == 200.0


def test_create_item_failure_already_exists(db_session: Session, create_test_user, create_test_category):
    """Test failure when creating an item that already exists."""
    item_data = schemas.ItemCreate(
        name="Test Item",
        description="Test Description",
        category=create_test_category.name,
        quantity=10,
        price=200.0
    )

    crud.create_item(db_session, item_data, creator_id=create_test_user.id)

    with pytest.raises(HTTPException) as exc_info:
        crud.create_item(db_session, item_data, creator_id=create_test_user.id)

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "Item already exists."


def test_create_item_failure_invalid_category(db_session: Session, create_test_user):
    """Test failure when creating an item with a non-existent category."""
    item_data = schemas.ItemCreate(
        name="Test Item",
        description="Test Description",
        category="Nonexistent Category",
        quantity=10,
        price=200.0
    )

    with pytest.raises(HTTPException) as exc_info:
        crud.create_item(db_session, item_data, creator_id=create_test_user.id)

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail["message"] == "This category does not exist! Create it first or choose an existing category."


def test_create_item_authorized(test_client, create_test_user, create_test_category, db_session):
    """Тест успешного создания элемента с авторизацией."""

    token = create_access_token(data={"sub": str(create_test_user.id)})
    headers = {"Authorization": f"Bearer {token}"}

    category_data = schemas.CategoryCreate(name="Cybernetic")
    category = crud.create_category(db=db_session, category=category_data)
    db_session.add(category)
    db_session.commit()

    item_data = {
        "name": "Test Item",
        "description": "Test Description",
        "category": category_data.name,
        "quantity": 10,
        "price": 200.0
    }

    response = test_client.post("/items/", json=item_data, headers=headers)

    assert response.status_code == 200
    created_item = response.json()
    assert created_item["name"] == "Test Item"
    assert created_item["description"] == "Test Description"
    assert created_item["category"] == category_data.name
    assert created_item["quantity"] == 10
    assert created_item["price"] == 200.0


def test_create_item_unauthorized(test_client, create_test_category, db_session):
    """Тест неуспешного создания элемента без авторизации."""

    category_data = schemas.CategoryCreate(name="Cybernetic")
    category = crud.create_category(db=db_session, category=category_data)
    db_session.add(category)
    db_session.commit()

    item_data = {
        "name": "Test Item",
        "description": "Test Description",
        "category": category_data.name,
        "quantity": 10,
        "price": 200.0
    }

    response = test_client.post("/items/", json=item_data)
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"


def test_update_item_description(db_session: Session, create_test_user, create_test_category, create_test_item):
    """Test updating the description of an existing item."""

    updated_data = schemas.ItemUpdateDescription(description="Updated Description")
    updated_item = crud.update_item_description(db_session, create_test_item.id, updated_data)

    assert updated_item.description == "Updated Description"

    with pytest.raises(HTTPException) as exc_info:
        crud.update_item_description(db_session, 999, updated_data)
    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Item not found."


def test_update_item_description_authorized(test_client, create_test_user, create_test_category, db_session):
    """Тест успешного обновления описания элемента с авторизацией."""

    token = create_access_token(data={"sub": str(create_test_user.id)})
    headers = {"Authorization": f"Bearer {token}"}

    item_data = schemas.ItemCreate(
        name="Test Item",
        description="Old Description",
        category=create_test_category.name,
        quantity=10,
        price=200.0
    )
    item = crud.create_item(db_session, item_data, creator_id=create_test_user.id)
    update_data = {"description": "New Description"}

    response = test_client.put(f"/items/{item.id}", json=update_data, headers=headers)

    assert response.status_code == 200
    updated_item = response.json()
    assert updated_item["description"] == "New Description"


def test_update_item_description_unauthorized(test_client, create_test_user, create_test_category, db_session):
    """Тест неуспешного обновления описания элемента без авторизации."""

    item_data = schemas.ItemCreate(
        name="Test Item",
        description="Old Description",
        category=create_test_category.name,
        quantity=10,
        price=200.0
    )
    item = crud.create_item(db_session, item_data, creator_id=create_test_user.id)
    update_data = {"description": "New Description"}

    response = test_client.put(f"/items/{item.id}", json=update_data)
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"


def test_delete_item(db_session: Session, create_test_user, create_test_category, create_test_item):
    """Test deleting an existing item."""

    deleted_item = crud.delete_item(db_session, create_test_item.id)
    assert deleted_item.id == create_test_item.id

    with pytest.raises(HTTPException) as exc_info:
        crud.delete_item(db_session, 999)
    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Item not found."


def test_delete_item_authorized(test_client, create_test_user, create_test_category, db_session):
    """Тест успешного удаления элемента с авторизацией."""

    token = create_access_token(data={"sub": str(create_test_user.id)})
    headers = {"Authorization": f"Bearer {token}"}

    item_data = schemas.ItemCreate(
        name="Test Item",
        description="Item to be deleted",
        category=create_test_category.name,
        quantity=10,
        price=200.0
    )
    item = crud.create_item(db_session, item_data, creator_id=create_test_user.id)

    response = test_client.delete(f"/items/{item.id}", headers=headers)
    assert response.status_code == 200
    deleted_item = response.json()
    assert deleted_item["id"] == item.id


def test_delete_item_unauthorized(test_client, create_test_user, create_test_category, db_session):
    """Тест неуспешного удаления элемента без авторизации."""

    item_data = schemas.ItemCreate(
        name="Test Item",
        description="Item to be deleted",
        category=create_test_category.name,
        quantity=10,
        price=200.0
    )
    item = crud.create_item(db_session, item_data, creator_id=create_test_user.id)

    response = test_client.delete(f"/items/{item.id}")
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"


def test_add_item_to_inventory(db_session: Session, create_test_user, create_test_item):
    """Test adding an item to the user's inventory."""

    added_item = crud.add_item_to_inventory(db_session, create_test_user.id, create_test_item.id)
    assert added_item.owner_id == create_test_user.id

    with pytest.raises(HTTPException) as exc_info:
        crud.add_item_to_inventory(db_session, create_test_user.id, create_test_item.id)
    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "Item already in user's inventory."

    with pytest.raises(HTTPException) as exc_info:
        crud.add_item_to_inventory(db_session, create_test_user.id, 999)
    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Item not found."


def test_remove_item_from_inventory(db_session: Session, create_test_user, create_test_item):
    """Test removing an item from the user's inventory."""

    crud.add_item_to_inventory(db_session, create_test_user.id, create_test_item.id)
    removed_item = crud.remove_item_from_inventory(db_session, create_test_user.id, create_test_item.id)
    assert removed_item.owner_id is None

    with pytest.raises(HTTPException) as exc_info:
        crud.remove_item_from_inventory(db_session, create_test_user.id, create_test_item.id)
    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Item not found in user's inventory."

    with pytest.raises(HTTPException) as exc_info:
        crud.remove_item_from_inventory(db_session, create_test_user.id, 999)
    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Item not found in user's inventory."


# Test pagination
def test_read_all_categories_pagination(test_client, db_session):
    """Test pagination for categories."""

    for i in range(10):
        category_data = schemas.CategoryCreate(name=f"Category {i}")
        crud.create_category(db=db_session, category=category_data)

    response = test_client.get("/categories/?page=1&limit=5")
    assert response.status_code == 200
    data = response.json()

    assert data["page"] == 1
    assert data["limit"] == 5
    assert data["total_items"] == 10
    assert data["total_pages"] == 2
    assert len(data["items"]) == 5
    assert data["next_page"] is not None
    assert data["prev_page"] is None

    response = test_client.get("/categories/?page=2&limit=5")
    assert response.status_code == 200
    data = response.json()

    assert data["page"] == 2
    assert len(data["items"]) == 5
    assert data["next_page"] is None
    assert data["prev_page"] is not None


def test_read_all_items_pagination(test_client, db_session, create_test_category, create_test_user):
    """Test pagination for items."""

    for i in range(10):
        item_data = schemas.ItemCreate(
            name=f"Item {i}",
            description=f"Description for Item {i}",
            category=create_test_category.name,
            quantity=10,
            price=100.0
        )
        crud.create_item(db=db_session, item=item_data, creator_id=create_test_user.id)

    response = test_client.get("/items/?page=1&limit=5")
    assert response.status_code == 200
    data = response.json()

    assert data["page"] == 1
    assert data["limit"] == 5
    assert data["total_items"] == 10
    assert data["total_pages"] == 2
    assert len(data["items"]) == 5
    assert data["next_page"] is not None
    assert data["prev_page"] is None

    response = test_client.get("/items/?page=2&limit=5")
    assert response.status_code == 200
    data = response.json()

    assert data["page"] == 2
    assert len(data["items"]) == 5
    assert data["next_page"] is None
    assert data["prev_page"] is not None


# Other
def test_app_initialization(test_client):
    """Test if the FastAPI app initializes successfully."""
    response = test_client.get("/")
    assert response.status_code == 200


def test_docs_available(test_client):
    """Test if the Swagger documentation is available."""
    response = test_client.get("/docs")
    assert response.status_code == 200

