from typing import List

from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.database import engine, get_db
from app.users.auth import verify_password, create_access_token, get_current_user
from app.users.crud import get_user_by_username, create_user
from app.users.models import User
from app.users.schemas import UserRead, UserCreate


models.Base.metadata.create_all(bind=engine)

app = FastAPI()


@app.post("/register", response_model=UserRead)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    return create_user(db=db, user=user)


@app.post("/token")
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = get_user_by_username(db, form_data.username)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    access_token = create_access_token(data={"sub": str(user.id)})
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/users/me", response_model=UserRead)
def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user


@app.get("/categories/", response_model=List[schemas.Category])
def read_categories(skip: int = 0, limit: int = 5, db: Session = Depends(get_db)):
    return crud.get_all_categories(db=db, skip=skip, limit=limit)


@app.post("/categories/", response_model=schemas.Category)
def create_category(category: schemas.CategoryCreate, db: Session = Depends(get_db)):
    db_category = crud.get_category_by_name(db=db, name=category.name)
    if db_category:
        raise HTTPException(status_code=400, detail="This category already exists.")
    return crud.create_category(db=db, category=category)


@app.delete("/categories/{category_id}", response_model=schemas.Category)
def delete_category(category_id: int, db: Session = Depends(get_db)):
    db_category = crud.delete_category(db=db, category_id=category_id)
    if db_category is None:
        raise HTTPException(status_code=404, detail="Category not found.")
    return db_category


@app.get("/items/{item_id}", response_model=schemas.ItemRead)
def read_item(item_id: int, db: Session = Depends(get_db)):
    db_item = crud.get_item_by_id(db=db, item_id=item_id)
    if db_item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return db_item


@app.get("/items/", response_model=List[schemas.ItemRead])
def read_items(skip: int = 0, limit: int = 5, db: Session = Depends(get_db)):
    items = crud.get_all_items(db=db, skip=skip, limit=limit)
    return items


@app.post("/items/", response_model=schemas.ItemRead)
def create_item(item: schemas.ItemCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_item = crud.get_item_by_name(db=db, name=item.name)
    if db_item:
        raise HTTPException(status_code=400, detail="Item already exists.")
    return crud.create_item(db=db, item=item, owner_id=current_user.id)


@app.put("/items/{item_id}", response_model=schemas.ItemRead)
def update_item(item_id: int, item: schemas.ItemCreate, db: Session = Depends(get_db)):
    db_item = crud.update_item(db=db, item_id=item_id, updated_item_data=item)
    if db_item is None:
        raise HTTPException(status_code=404, detail="Item not found.")
    return db_item


@app.delete("/items/{item_id}", response_model=schemas.ItemRead)
def delete_item(item_id: int, db: Session = Depends(get_db)):
    db_item = crud.delete_item(db=db, item_id=item_id)
    if db_item is None:
        raise HTTPException(status_code=404, detail="Item not found.")
    return db_item
