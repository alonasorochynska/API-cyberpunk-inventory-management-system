from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from inventory import crud, schemas
from database import get_db
from pagination import paginate, PaginatedResponse
from users.auth import get_current_user
from users.models import User


router = APIRouter()


@router.get("/categories/", response_model=PaginatedResponse[schemas.Category])
def read_all_categories(page: int = 1, limit: int = 5, db: Session = Depends(get_db), request: Request = None):
    query = crud.get_all_categories_query(db=db)
    return paginate(query, page, limit, request)


@router.post("/categories/", response_model=schemas.Category)
def create_category(category: schemas.CategoryCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return crud.create_category(db=db, category=category)


@router.delete("/categories/{category_id}", response_model=schemas.Category)
def remove_category(category_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_category = crud.delete_category(db=db, category_id=category_id)
    return db_category


@router.get("/items/{item_id}", response_model=schemas.ItemRead)
def read_item(item_id: int, db: Session = Depends(get_db)):
    return crud.get_item_by_id(db=db, item_id=item_id)


@router.get("/items/", response_model=PaginatedResponse[schemas.ItemRead])
def read_all_items(page: int = 1, limit: int = 5, db: Session = Depends(get_db), request: Request = None):
    query = crud.get_all_items_query(db=db)
    return paginate(query, page, limit, request)


@router.post("/items/", response_model=schemas.ItemRead)
def create_item(item: schemas.ItemCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return crud.create_item(db=db, item=item, creator_id=current_user.id)


@router.put("/items/{item_id}", response_model=schemas.ItemRead)
def update_item(item_id: int, item: schemas.ItemUpdateDescription, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_item = crud.update_item_description(db=db, item_id=item_id, updated_item_data=item)
    return db_item


@router.delete("/items/{item_id}", response_model=schemas.ItemRead)
def remove_item(item_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_item = crud.delete_item(db=db, item_id=item_id)
    return db_item


@router.post("/inventory/add/{item_id}")
def assign_item_to_user_inventory(item_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return crud.add_item_to_inventory(db=db, user_id=current_user.id, item_id=item_id)


@router.delete("/inventory/remove/{item_id}")
def remove_item_from_user_inventory(item_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return crud.remove_item_from_inventory(db=db, user_id=current_user.id, item_id=item_id)