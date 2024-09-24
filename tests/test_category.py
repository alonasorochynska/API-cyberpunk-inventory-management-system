import pytest
from fastapi import HTTPException
from sqlalchemy.orm import Session
from starlette.testclient import TestClient

from inventory import schemas, crud, models
from users.auth import create_access_token
from users.models import User


def test_create_category(db_session: Session):
    """Test creating a new category."""
    category_data = schemas.CategoryCreate(name="Cybernetic")
    category = crud.create_category(db=db_session, category=category_data)

    assert category.name == "Cybernetic"


def test_create_category_duplicate(db_session: Session):
    """Test handling duplicate category creation."""
    category_data = schemas.CategoryCreate(name="Cybernetic")
    crud.create_category(db=db_session, category=category_data)

    with pytest.raises(HTTPException) as exc_info:
        crud.create_category(db=db_session, category=category_data)

    assert exc_info.value.status_code == 400
    assert "Category with this name already exists." in str(
        exc_info.value.detail
    )


def test_create_category_authorized(
        test_client: TestClient,
        create_test_user: User
):
    """Test creating a category with authorization."""
    token = create_access_token(data={"sub": str(create_test_user.id)})

    headers = {
        "Authorization": f"Bearer {token}"
    }

    category_data = {"name": "Cybernetic"}
    response = test_client.post(
        "/categories/", json=category_data, headers=headers
    )

    assert response.status_code == 200
    assert response.json()["name"] == "Cybernetic"


def test_create_category_unauthorized(test_client: TestClient):
    """Test creating a category without authorization."""
    category_data = {"name": "Cybernetic"}
    response = test_client.post("/categories/", json=category_data)

    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"


def test_get_category_by_name(db_session: Session):
    """Test retrieving a category by name."""
    category_data = schemas.CategoryCreate(name="Cybernetic")
    crud.create_category(db=db_session, category=category_data)
    category = crud.get_category_by_name(db=db_session, name="Cybernetic")

    assert category is not None
    assert category.name == "Cybernetic"


def test_delete_category(db_session: Session):
    """Test deleting a category."""
    category_data = schemas.CategoryCreate(name="Cybernetic")
    category = crud.create_category(db=db_session, category=category_data)
    deleted_category = crud.delete_category(
        db=db_session, category_id=category.id
    )

    assert deleted_category is not None
    assert deleted_category.name == "Cybernetic"


def test_delete_category_authorized(
        test_client: TestClient, create_test_user: User, db_session: Session
):
    """Test deleting a category with authorization."""
    token = create_access_token(data={"sub": str(create_test_user.id)})
    headers = {"Authorization": f"Bearer {token}"}

    category_data = {"name": "Cybernetic"}
    response = test_client.post(
        "/categories/", json=category_data, headers=headers
    )

    assert response.status_code == 200
    created_category = response.json()

    response = test_client.delete(
        f"/categories/{created_category['id']}", headers=headers
    )

    assert response.status_code == 200
    deleted_category = response.json()
    assert deleted_category["name"] == "Cybernetic"


def test_delete_category_unauthorized(
        test_client: TestClient, db_session: Session
):
    """Test deleting a category without authorization."""
    category_data = schemas.CategoryCreate(name="Cybernetic")
    category = crud.create_category(db=db_session, category=category_data)

    response = test_client.delete(f"/categories/{category.id}")

    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"


def test_get_all_categories_query(db_session: Session):
    """Test retrieving all categories."""
    category1 = models.Category(name="Category 1")
    category2 = models.Category(name="Category 2")

    db_session.add_all([category1, category2])
    db_session.commit()

    result = crud.get_all_categories_query(db=db_session).all()

    assert len(result) == 2
    assert result[0].name == "Category 1"
    assert result[1].name == "Category 2"
