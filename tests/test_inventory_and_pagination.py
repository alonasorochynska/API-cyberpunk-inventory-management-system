import pytest
from fastapi import HTTPException
from sqlalchemy.orm import Session

from inventory import schemas, crud, models
from fastapi.testclient import TestClient
from users.models import User


def test_add_item_to_inventory(
        db_session: Session,
        create_test_user: User,
        create_test_item: models.Item
):
    """Test adding an item to the user's inventory."""
    added_item = crud.add_item_to_inventory(
        db=db_session, user_id=create_test_user.id, item_id=create_test_item.id
    )
    assert added_item.owner_id == create_test_user.id

    with pytest.raises(HTTPException) as exc_info:
        crud.add_item_to_inventory(
            db=db_session,
            user_id=create_test_user.id,
            item_id=create_test_item.id
        )
    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "Item already in user's inventory."

    with pytest.raises(HTTPException) as exc_info:
        crud.add_item_to_inventory(
            db=db_session, user_id=create_test_user.id, item_id=999
        )
    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Item not found."


def test_remove_item_from_inventory(
        db_session: Session,
        create_test_user: User,
        create_test_item: models.Item
):
    """Test removing an item from the user's inventory."""
    crud.add_item_to_inventory(
        db=db_session, user_id=create_test_user.id, item_id=create_test_item.id
    )
    removed_item = crud.remove_item_from_inventory(
        db=db_session, user_id=create_test_user.id, item_id=create_test_item.id
    )
    assert removed_item.owner_id is None

    with pytest.raises(HTTPException) as exc_info:
        crud.remove_item_from_inventory(
            db=db_session,
            user_id=create_test_user.id,
            item_id=create_test_item.id
        )
    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Item not found in user's inventory."

    with pytest.raises(HTTPException) as exc_info:
        crud.remove_item_from_inventory(
            db=db_session, user_id=create_test_user.id, item_id=999
        )
    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Item not found in user's inventory."


def test_read_all_categories_pagination(
        test_client: TestClient,
        db_session: Session
):
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


def test_read_all_items_pagination(
        test_client: TestClient,
        db_session: Session,
        create_test_category: models.Category,
        create_test_user: User
):
    """Test pagination for items."""
    for i in range(10):
        item_data = schemas.ItemCreate(
            name=f"Item {i}",
            description=f"Description for Item {i}",
            category=create_test_category.name,
            quantity=10,
            price=100.0
        )
        crud.create_item(
            db=db_session, item=item_data, creator_id=create_test_user.id
        )

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


def test_app_initialization(test_client: TestClient):
    """Test if the FastAPI app initializes successfully."""
    response = test_client.get("/")
    assert response.status_code == 200


def test_docs_swagger_available(test_client: TestClient):
    """Test if the Swagger documentation is available."""
    response = test_client.get("/docs")
    assert response.status_code == 200


def test_docs_redoc_available(test_client: TestClient):
    """Test if the ReDoc documentation is available."""
    response = test_client.get("/redoc")
    assert response.status_code == 200
