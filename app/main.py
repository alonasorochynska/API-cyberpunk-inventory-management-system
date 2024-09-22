from fastapi import FastAPI, Depends, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.database import engine, get_db
from app.pagination import paginate, PaginatedResponse
from app.users.auth import get_current_user
from app.users.crud import create_user, authenticate_user
from app.users.models import User
from app.users.schemas import UserRead, UserCreate


models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Cyberpunk Inventory Management API",
    description="This system manages the items that players can acquire in the game.",
    version="1.0.0",
    contact={
        "name": "Alona",
        "email": "alona.sorochynska.job@gmail.com",
    },
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT",
    }
)


@app.get("/")
def welcome_message():
    return {
        "message": "Welcome to the Cyberpunk Inventory Management System API!",
        "info": "Use this API to manage users, items, and inventory. Access token "
                "authentication is required for most operations.",
        "endpoints": {
            "register": "/register",
            "login": "/token",
            "get_current_user": "/users/me",
            "get_items": "/items/",
            "get_categories": "/categories/",
            "documentation": "/docs"
        },
        "note": "You can explore and test the API through the interactive documentation "
                "available at /docs."
    }


@app.post("/register", response_model=UserRead)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    return create_user(db=db, user=user)


@app.post("/token")
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    access_token = authenticate_user(db=db, username=form_data.username, password=form_data.password)
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/users/me", response_model=UserRead)
def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user


@app.get("/categories/", response_model=PaginatedResponse[schemas.Category])
def read_all_categories(page: int = 1, limit: int = 5, db: Session = Depends(get_db), request: Request = None):
    query = crud.get_all_categories_query(db=db)
    return paginate(query, page, limit, request)


@app.post("/categories/", response_model=schemas.Category)
def create_category(category: schemas.CategoryCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return crud.create_category(db=db, category=category)


@app.delete("/categories/{category_id}", response_model=schemas.Category)
def remove_category(category_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_category = crud.delete_category(db=db, category_id=category_id)
    return db_category


@app.get("/items/{item_id}", response_model=schemas.ItemRead)
def read_item(item_id: int, db: Session = Depends(get_db)):
    return crud.get_item_by_id(db=db, item_id=item_id)


@app.get("/items/", response_model=PaginatedResponse[schemas.ItemRead])
def read_all_items(page: int = 1, limit: int = 5, db: Session = Depends(get_db), request: Request = None):
    query = crud.get_all_items_query(db=db)
    return paginate(query, page, limit, request)


@app.post("/items/", response_model=schemas.ItemRead)
def create_item(item: schemas.ItemCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return crud.create_item(db=db, item=item, creator_id=current_user.id)


@app.put("/items/{item_id}", response_model=schemas.ItemRead)
def update_item(item_id: int, item: schemas.ItemUpdateDescription, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_item = crud.update_item_description(db=db, item_id=item_id, updated_item_data=item)
    return db_item


@app.delete("/items/{item_id}", response_model=schemas.ItemRead)
def remove_item(item_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_item = crud.delete_item(db=db, item_id=item_id)
    return db_item


@app.post("/inventory/add/{item_id}")
def assign_item_to_user_inventory(item_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return crud.add_item_to_inventory(db=db, user_id=current_user.id, item_id=item_id)


@app.delete("/inventory/remove/{item_id}")
def remove_item_from_user_inventory(item_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return crud.remove_item_from_inventory(db=db, user_id=current_user.id, item_id=item_id)
