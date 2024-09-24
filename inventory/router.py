from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from database import get_db
from inventory import crud, models, schemas
from pagination import paginate, PaginatedResponse
from users.auth import get_current_user
from users.models import User


router = APIRouter()


@router.get(
    "/categories/",
    response_model=PaginatedResponse[schemas.Category],
    tags=["categories"]
)
def read_all_categories(
        page: int = 1,
        limit: int = 5,
        db: Session = Depends(get_db),
        request: Request = None
) -> PaginatedResponse[schemas.Category]:
    """
    Retrieve a paginated list of categories.
    """
    query = crud.get_all_categories_query(db=db)
    return paginate(query=query, page=page, limit=limit, request=request)


@router.post(
    "/categories/",
    response_model=schemas.Category,
    tags=["categories"]
)
def create_category(
        category: schemas.CategoryCreate,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
) -> schemas.Category:
    """
    Create a new category in the database.
    """
    return crud.create_category(db=db, category=category)


@router.delete(
    "/categories/{category_id}",
    response_model=schemas.Category,
    tags=["categories"]
)
def remove_category(
        category_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
) -> schemas.Category:
    """
    Delete a category by ID.
    """
    db_category = crud.delete_category(db=db, category_id=category_id)
    return db_category


@router.get(
    "/items/{item_id}", response_model=schemas.ItemRead, tags=["items"]
)
def read_item(
        item_id: int,
        db: Session = Depends(get_db)
) -> models.Item:
    """
    Retrieve an item by its ID.
    """
    return crud.get_item_by_id(db=db, item_id=item_id)


@router.get(
    "/items/",
    response_model=PaginatedResponse[schemas.ItemRead],
    tags=["items"]
)
def read_all_items(
        page: int = 1,
        limit: int = 5,
        db: Session = Depends(get_db),
        request: Request = None
) -> PaginatedResponse[schemas.ItemRead]:
    """
    Retrieve a paginated list of items.
    """
    query = crud.get_all_items_query(db=db)
    return paginate(query=query, page=page, limit=limit, request=request)


@router.post("/items/", response_model=schemas.ItemRead, tags=["items"])
def create_item(
        item: schemas.ItemCreate,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
) -> models.Item:
    """
    Create a new item.
    """
    return crud.create_item(db=db, item=item, creator_id=current_user.id)


@router.put(
    "/items/{item_id}",
    response_model=schemas.ItemRead,
    tags=["items"]
)
def update_item(
        item_id: int,
        item: schemas.ItemUpdateDescription,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
) -> models.Item:
    """
    Update an item's description.
    """
    db_item = crud.update_item_description(
        db=db, item_id=item_id, updated_item_data=item
    )
    return db_item


@router.delete(
    "/items/{item_id}",
    response_model=schemas.ItemRead,
    tags=["items"]
)
def remove_item(
        item_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
) -> models.Item:
    """
    Delete an item by ID.
    """
    db_item = crud.delete_item(db=db, item_id=item_id)
    return db_item


@router.post(
    "/inventory/add/{item_id}",
    response_model=schemas.ItemRead,
    tags=["inventory"]
)
def assign_item_to_user_inventory(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> schemas.ItemRead:
    """
    Assign an item to the current user's inventory.
    """
    item = crud.add_item_to_inventory(
        db=db, user_id=current_user.id, item_id=item_id
    )
    return schemas.ItemRead.model_validate(item)


@router.delete("/inventory/remove/{item_id}", tags=["inventory"])
def remove_item_from_user_inventory(
        item_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
) -> schemas.ItemRead:
    """
    Remove an item from the current user's inventory.
    """
    item = crud.remove_item_from_inventory(
        db=db, user_id=current_user.id, item_id=item_id
    )
    return schemas.ItemRead.model_validate(item)
