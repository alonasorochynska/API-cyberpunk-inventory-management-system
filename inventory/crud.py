from fastapi import HTTPException
from sqlalchemy.orm import Session, Query

from inventory import models, schemas
from typing import Optional


def get_category_by_name(db: Session, name: str) -> Optional[models.Category]:
    """
    Retrieve a category by its name from the database.
    """
    return db.query(models.Category).filter(
        models.Category.name == name
    ).first()


def get_all_categories_query(db: Session) -> Query:
    """
    Retrieve all categories query.
    """
    return db.query(models.Category)


def create_category(
        db: Session,
        category: schemas.CategoryCreate
) -> models.Category:
    """
    Create a new category in the database.
    """
    db_category = get_category_by_name(db=db, name=category.name)
    if db_category:
        raise HTTPException(
            status_code=400, detail="Category with this name already exists."
        )

    new_category = models.Category(name=category.name)
    db.add(new_category)
    db.commit()
    db.refresh(new_category)
    return new_category


def delete_category(db: Session, category_id: int) -> models.Category:
    """
    Delete a category by its ID.
    """
    db_category = db.query(models.Category).filter(
        models.Category.id == category_id
    ).first()
    if not db_category:
        raise HTTPException(status_code=404, detail="Category not found.")

    db.delete(db_category)
    db.commit()
    return db_category


def get_item_by_id(db: Session, item_id: int) -> models.Item:
    """
    Retrieve an item by its ID.
    """
    db_item = db.query(models.Item).filter(models.Item.id == item_id).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found.")
    return db_item


def get_item_by_name(db: Session, name: str) -> Optional[models.Item]:
    """
    Retrieve an item by its name.
    """
    return db.query(models.Item).filter(models.Item.name == name).first()


def get_all_items_query(db: Session) -> Query:
    """
    Retrieve all items query.
    """
    return db.query(models.Item)


def validate_category_exists(db: Session, category_name: str) -> None:
    """
    Validate if a category exists by name, otherwise raise an error.
    """
    category = get_category_by_name(db=db, name=category_name)
    if not category:
        existing_categories = get_all_categories_query(db=db).all()
        existing_category_names = [
            category.name for category in existing_categories
        ]

        raise HTTPException(
            status_code=400,
            detail={
                "message": "This category does not exist! Create it first "
                           "or choose an existing category.",
                "existing_categories": existing_category_names
            }
        )


def create_item(
        db: Session,
        item: schemas.ItemCreate,
        creator_id: int
) -> models.Item:
    """
    Create a new item in the database.
    """
    db_item = get_item_by_name(db=db, name=item.name)
    if db_item:
        raise HTTPException(status_code=400, detail="Item already exists.")

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


def update_item_description(
        db: Session,
        item_id: int,
        updated_item_data: schemas.ItemUpdateDescription
) -> models.Item:
    """
    Update the description of an existing item.
    """
    db_item = db.query(models.Item).filter(models.Item.id == item_id).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found.")

    if updated_item_data.description is not None:
        db_item.description = updated_item_data.description
        db.commit()
        db.refresh(db_item)

    return db_item


def delete_item(db: Session, item_id: int) -> models.Item:
    """
    Delete an item by its ID.
    """
    db_item = db.query(models.Item).filter(models.Item.id == item_id).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found.")

    db.delete(db_item)
    db.commit()
    return db_item


def add_item_to_inventory(
        db: Session,
        user_id: int,
        item_id: int
) -> models.Item:
    """
    Assign an item to the user's inventory.
    """
    item = db.query(models.Item).filter(models.Item.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found.")

    if item.owner_id == user_id:
        raise HTTPException(
            status_code=400, detail="Item already in user's inventory."
        )

    item.owner_id = user_id
    db.commit()
    db.refresh(item)
    return item


def remove_item_from_inventory(
        db: Session,
        user_id: int,
        item_id: int
) -> models.Item:
    """
    Remove an item from the user's inventory.
    """
    item = db.query(models.Item).filter(
        models.Item.id == item_id, models.Item.owner_id == user_id
    ).first()
    if not item:
        raise HTTPException(
            status_code=404, detail="Item not found in user's inventory."
        )

    item.owner_id = None
    db.commit()
    db.refresh(item)
    return item
