from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.database import engine, get_db
from app.pagination import paginate, PaginatedResponse
from app.users.auth import verify_password, create_access_token, get_current_user
from app.users.crud import get_user_by_username, create_user, check_user_existence_by_username_or_email
from app.users.models import User
from app.users.schemas import UserRead, UserCreate


models.Base.metadata.create_all(bind=engine)

app = FastAPI()


@app.post("/register", response_model=UserRead)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user_by_username = check_user_existence_by_username_or_email(db=db, field_name="username", value=user.username)
    if db_user_by_username:
        raise HTTPException(status_code=400, detail="This username already registered")

    db_user_by_email = check_user_existence_by_username_or_email(db=db, field_name="email", value=user.email)
    if db_user_by_email:
        raise HTTPException(status_code=400, detail="This email already registered")

    return create_user(db=db, user=user)


@app.post("/token")
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = get_user_by_username(db=db, username=form_data.username)
    if not user or not verify_password(plain_password=form_data.password, hashed_password=user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    access_token = create_access_token(data={"sub": str(user.id)})
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

