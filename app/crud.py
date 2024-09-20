from fastapi import HTTPException
from sqlalchemy.orm import Session

from app import models, schemas


def get_category_by_name(db: Session, name: str):
    return db.query(models.Category).filter(models.Category.name == name).first()


def get_all_categories(db: Session, skip: int = 0, limit: int = 5):
    return db.query(models.Category).offset(skip).limit(limit).all()


def create_category(db: Session, category: schemas.CategoryCreate):
    db_category = models.Category(name=category.name)
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category


def delete_category(db: Session, category_id: int):
    db_category = db.query(models.Category).filter(models.Category.id == category_id).first()
    if db_category:
        db.delete(db_category)
        db.commit()
    return db_category


def get_item_by_id(db: Session, item_id: int):
    return db.query(models.Item).filter(models.Item.id == item_id).first()


def get_item_by_name(db: Session, name: str):
    return db.query(models.Item).filter(models.Item.name == name).first()


def get_all_items(db: Session, skip: int = 0, limit: int = 5):
    return db.query(models.Item).offset(skip).limit(limit).all()


def validate_category_exists(db: Session, category_name: str):
    category = get_category_by_name(db=db, name=category_name)
    if not category:
        raise HTTPException(status_code=400, detail="This category does not exist! Create it first.")


def create_item(db: Session, item: schemas.ItemCreate):
    validate_category_exists(db=db, category_name=item.category)
    db_item = models.Item(
        name=item.name,
        description=item.description,
        category=item.category,
        quantity=item.quantity,
        price=item.price,
    )
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


def update_item(db: Session, item_id: int, updated_item_data: schemas.ItemCreate):

    db_item = db.query(models.Item).filter(models.Item.id == item_id).first()
    if db_item:
        validate_category_exists(db=db, category_name=updated_item_data.category)
        update_data = updated_item_data.model_dump()
        for key, value in update_data.items():
            setattr(db_item, key, value)
        db.commit()
        db.refresh(db_item)
    return db_item


def delete_item(db: Session, item_id: int):
    db_item = db.query(models.Item).filter(models.Item.id == item_id).first()
    if db_item:
        db.delete(db_item)
        db.commit()
    return db_item
