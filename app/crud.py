from fastapi import HTTPException
from sqlalchemy.orm import Session

from app import models, schemas


def get_category_by_name(db: Session, name: str):
    return db.query(models.Category).filter(models.Category.name == name).first()


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


def validate_category_exists(db: Session, category_name: str):
    category = get_category_by_name(db=db, name=category_name)
    if not category:
        raise HTTPException(status_code=400, detail="This category does not exist! Create it first.")


def create_item(db: Session, item: schemas.ItemCreate, creator_id: int):
    validate_category_exists(db=db, category_name=item.category)
    db_item = models.Item(
        name=item.name,
        description=item.description,
        category=item.category,
        quantity=item.quantity,
        price=item.price,
        creator_id=creator_id,
    )
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


def update_item_description(db: Session, item_id: int, updated_item_data: schemas.ItemUpdateDescription):
    db_item = db.query(models.Item).filter(models.Item.id == item_id).first()

    if db_item and updated_item_data.description is not None:
        db_item.description = updated_item_data.description

        db.commit()
        db.refresh(db_item)

    return db_item


def delete_item(db: Session, item_id: int):
    db_item = db.query(models.Item).filter(models.Item.id == item_id).first()
    if db_item:
        db.delete(db_item)
        db.commit()
    return db_item


def add_item_to_inventory(db: Session, user_id: int, item_id: int):
    item = db.query(models.Item).filter(models.Item.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    if item.owner_id == user_id:
        raise HTTPException(status_code=400, detail="Item already in user's inventory")

    item.owner_id = user_id
    db.commit()
    db.refresh(item)
    return item


def remove_item_from_inventory(db: Session, user_id: int, item_id: int):
    item = db.query(models.Item).filter(models.Item.id == item_id, models.Item.owner_id == user_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found in user's inventory")

    item.owner_id = None
    db.commit()
    db.refresh(item)
    return item
