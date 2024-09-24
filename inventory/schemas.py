from pydantic import BaseModel
from typing import Optional


class CategoryBase(BaseModel):
    """Base model for Category with common fields."""
    name: str

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Weapon"
            }
        }


class CategoryCreate(CategoryBase):
    """Model for creating a new Category."""
    pass


class Category(CategoryBase):
    """Model representing a Category with ID."""
    id: int

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "name": "Weapon"
            }
        }


class ItemBase(BaseModel):
    """Base model for Item in a cyberpunk-themed game."""
    name: str
    description: Optional[str] = None
    category: str
    quantity: int
    price: Optional[float] = 0.0

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Laser Rifle",
                "description": "A high-tech weapon "
                               "capable of firing plasma rounds.",
                "category": "Weapon",
                "quantity": 5,
                "price": 3000.0
            }
        }


class ItemCreate(ItemBase):
    """Model for creating a new Item."""
    pass


class ItemRead(ItemBase):
    """Model for reading an Item with additional fields."""
    id: int
    creator_id: int
    owner_id: Optional[int] = None

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 101,
                "name": "Laser Rifle",
                "description": "A high-tech weapon "
                               "capable of firing plasma rounds.",
                "category": "Weapon",
                "quantity": 5,
                "price": 3000.0,
                "creator_id": 1,
                "owner_id": 2
            }
        }


class ItemUpdateDescription(BaseModel):
    """Model for updating the description of an Item."""
    description: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "description": "Updated description for the weapon."
            }
        }
