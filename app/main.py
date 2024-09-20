from typing import List

from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


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


@app.get("/items/{item_id}", response_model=schemas.Item)
def read_item(item_id: int, db: Session = Depends(get_db)):
    db_item = crud.get_item_by_id(db=db, item_id=item_id)
    if db_item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return db_item


@app.get("/items/", response_model=List[schemas.Item])
def read_items(skip: int = 0, limit: int = 5, db: Session = Depends(get_db)):
    items = crud.get_all_items(db=db, skip=skip, limit=limit)
    return items


@app.post("/items/", response_model=schemas.Item)
def create_item(item: schemas.ItemCreate, db: Session = Depends(get_db)):
    db_item = crud.get_item_by_name(db=db, name=item.name)
    if db_item:
        raise HTTPException(status_code=400, detail="Item already exists.")
    return crud.create_item(db=db, item=item)


@app.put("/items/{item_id}", response_model=schemas.Item)
def update_item(item_id: int, item: schemas.ItemCreate, db: Session = Depends(get_db)):
    db_item = crud.update_item(db=db, item_id=item_id, updated_item_data=item)
    if db_item is None:
        raise HTTPException(status_code=404, detail="Item not found.")
    return db_item


@app.delete("/items/{item_id}", response_model=schemas.Item)
def delete_item(item_id: int, db: Session = Depends(get_db)):
    db_item = crud.delete_item(db=db, item_id=item_id)
    if db_item is None:
        raise HTTPException(status_code=404, detail="Item not found.")
    return db_item
