import pytest
from fastapi import HTTPException
from sqlalchemy.orm import Session
from starlette.testclient import TestClient

from inventory import schemas, crud, models
from users.auth import create_access_token
from users.models import User


def test_get_item_by_id(db_session: Session, create_test_item: models.Item):
    """Test for getting an item by its ID."""
    result = crud.get_item_by_id(db=db_session, item_id=create_test_item.id)

    assert result.name == "Test Item"
    assert result.description == "Test Description"
    assert result.category == create_test_item.category

    with pytest.raises(HTTPException) as exc_info:
        crud.get_item_by_id(db=db_session, item_id=999)

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Item not found."


def test_get_item_by_name(db_session: Session, create_test_item: models.Item):
    """Test for getting an item by its name."""
    result = crud.get_item_by_name(db=db_session, name=create_test_item.name)

    assert result is not None
    assert result.name == "Test Item"
    assert result.description == "Test Description"

    result = crud.get_item_by_name(db=db_session, name="Nonexistent Item")
    assert result is None


def test_get_all_items_query(
    db_session: Session,
        create_test_user: User,
        create_test_category: models.Category
):
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

    query = crud.get_all_items_query(db=db_session)
    items = query.all()

    assert len(items) == 2
    assert items[0].name == "Test Item 1"
    assert items[1].name == "Test Item 2"


def test_validate_category_exists_success(
        db_session: Session,
        create_test_category: models.Category
):
    """Test successful validation of an existing category."""
    try:
        crud.validate_category_exists(
            db=db_session, category_name=create_test_category.name
        )
    except HTTPException:
        pytest.fail(
            "HTTPException raised unexpectedly for existing category"
        )


def test_validate_category_exists_failure(db_session: Session):
    """Test validation failure for non-existing category."""
    with pytest.raises(HTTPException) as exc_info:
        crud.validate_category_exists(
            db=db_session, category_name="Nonexistent Category"
        )

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail["message"] == (
        "This category does not exist! "
        "Create it first or choose an existing category."
    )
    assert "existing_categories" in exc_info.value.detail


def test_create_item_success(
    db_session: Session,
        create_test_user: User,
        create_test_category: models.Category
):
    """Test successful item creation."""
    item_data = schemas.ItemCreate(
        name="Test Item",
        description="Test Description",
        category=create_test_category.name,
        quantity=10,
        price=200.0
    )

    item = crud.create_item(
        db=db_session, item=item_data, creator_id=create_test_user.id
    )

    assert item.name == "Test Item"
    assert item.description == "Test Description"
    assert item.category == create_test_category.name
    assert item.quantity == 10
    assert item.price == 200.0


def test_create_item_failure_already_exists(
    db_session: Session,
        create_test_user: User,
        create_test_category: models.Category
):
    """Test failure when creating an item that already exists."""
    item_data = schemas.ItemCreate(
        name="Test Item",
        description="Test Description",
        category=create_test_category.name,
        quantity=10,
        price=200.0
    )

    crud.create_item(
        db=db_session, item=item_data, creator_id=create_test_user.id
    )

    with pytest.raises(HTTPException) as exc_info:
        crud.create_item(
            db=db_session, item=item_data, creator_id=create_test_user.id
        )

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "Item already exists."


def test_create_item_failure_invalid_category(
        db_session: Session,
        create_test_user: User
):
    """Test failure when creating an item with a non-existent category."""
    item_data = schemas.ItemCreate(
        name="Test Item",
        description="Test Description",
        category="Nonexistent Category",
        quantity=10,
        price=200.0
    )

    with pytest.raises(HTTPException) as exc_info:
        crud.create_item(
            db=db_session, item=item_data, creator_id=create_test_user.id
        )

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail["message"] == (
        "This category does not exist! "
        "Create it first or choose an existing category."
    )


def test_create_item_authorized(
    test_client,
        create_test_user: User,
        create_test_category: models.Category,
        db_session: Session
):
    """Test successful item creation with authorization."""
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


def test_create_item_unauthorized(
        test_client,
        create_test_category: models.Category,
        db_session: Session
):
    """Test unsuccessful item creation without authorization."""
    item_data = {
        "name": "Test Item",
        "description": "Test Description",
        "category": create_test_category.name,
        "quantity": 10,
        "price": 200.0
    }

    response = test_client.post("/items/", json=item_data)

    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"


def test_update_item_description(
    db_session: Session,
        create_test_user: User,
        create_test_category: models.Category,
        create_test_item: models.Item
):
    """Test updating the description of an existing item."""
    updated_data = schemas.ItemUpdateDescription(
        description="Updated Description"
    )
    updated_item = crud.update_item_description(
        db=db_session,
        item_id=create_test_item.id,
        updated_item_data=updated_data
    )

    assert updated_item.description == "Updated Description"

    with pytest.raises(HTTPException) as exc_info:
        crud.update_item_description(
            db=db_session, item_id=999, updated_item_data=updated_data
        )

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Item not found."


def test_update_item_description_authorized(
        test_client: TestClient,
        create_test_user: User,
        create_test_category: models.Category,
        db_session: Session
):
    """Test successful update of item description with authorization."""
    token = create_access_token(data={"sub": str(create_test_user.id)})
    headers = {"Authorization": f"Bearer {token}"}

    item_data = schemas.ItemCreate(
        name="Test Item",
        description="Old Description",
        category=create_test_category.name,
        quantity=10,
        price=200.0
    )
    item = crud.create_item(
        db=db_session,
        item=item_data,
        creator_id=create_test_user.id
    )
    update_data = {"description": "New Description"}

    response = test_client.put(
        url=f"/items/{item.id}",
        json=update_data,
        headers=headers
    )

    assert response.status_code == 200
    updated_item = response.json()
    assert updated_item["description"] == "New Description"


def test_update_item_description_unauthorized(
        test_client: TestClient,
        create_test_user: User,
        create_test_category: models.Category,
        db_session: Session
):
    """Test failed update of item description without authorization."""
    item_data = schemas.ItemCreate(
        name="Test Item",
        description="Old Description",
        category=create_test_category.name,
        quantity=10,
        price=200.0
    )
    item = crud.create_item(
        db=db_session,
        item=item_data,
        creator_id=create_test_user.id
    )
    update_data = {"description": "New Description"}

    response = test_client.put(
        url=f"/items/{item.id}",
        json=update_data
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"


def test_delete_item(
        db_session: Session,
        create_test_user: User,
        create_test_category: models.Category,
        create_test_item: models.Item
):
    """Test deleting an existing item."""
    deleted_item = crud.delete_item(db=db_session, item_id=create_test_item.id)

    assert deleted_item.id == create_test_item.id

    with pytest.raises(HTTPException) as exc_info:
        crud.delete_item(db=db_session, item_id=999)

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Item not found."


def test_delete_item_authorized(
        test_client: TestClient,
        create_test_user: User,
        create_test_category: models.Category,
        db_session: Session
):
    """Test successful deletion of an item with authorization."""
    token = create_access_token(data={"sub": str(create_test_user.id)})
    headers = {"Authorization": f"Bearer {token}"}

    item_data = schemas.ItemCreate(
        name="Test Item",
        description="Item to be deleted",
        category=create_test_category.name,
        quantity=10,
        price=200.0
    )
    item = crud.create_item(
        db=db_session,
        item=item_data,
        creator_id=create_test_user.id
    )

    response = test_client.delete(
        url=f"/items/{item.id}",
        headers=headers
    )
    assert response.status_code == 200
    deleted_item = response.json()
    assert deleted_item["id"] == item.id


def test_delete_item_unauthorized(
        test_client: TestClient,
        create_test_user: User,
        create_test_category: models.Category,
        db_session: Session
):
    """Test failed deletion of an item without authorization."""
    item_data = schemas.ItemCreate(
        name="Test Item",
        description="Item to be deleted",
        category=create_test_category.name,
        quantity=10,
        price=200.0
    )
    item = crud.create_item(
        db=db_session,
        item=item_data,
        creator_id=create_test_user.id
    )

    response = test_client.delete(url=f"/items/{item.id}")
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"
