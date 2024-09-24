from typing import List
from pydantic import BaseModel, EmailStr

from inventory.schemas import ItemRead


class UserBase(BaseModel):
    """Base user model with common fields."""
    username: str
    email: EmailStr

    class Config:
        json_schema_extra = {
            "example": {
                "username": "cyberpunk_rider",
                "email": "rider@cyberpunk.com"
            }
        }


class UserCreate(UserBase):
    """Model for creating a new user."""
    password: str

    class Config:
        json_schema_extra = {
            "example": {
                "username": "cyberpunk_rider",
                "email": "rider@cyberpunk.com",
                "password": "securepassword123"
            }
        }


class UserRead(UserBase):
    """Model for reading user data including inventory."""
    id: int
    is_active: bool
    is_superuser: bool
    inventory: List[ItemRead]

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 42,
                "username": "cyberpunk_rider",
                "email": "rider@cyberpunk.com",
                "is_active": True,
                "is_superuser": False,
                "inventory": [
                    {
                        "id": 101,
                        "name": "Laser Rifle",
                        "description": "A powerful weapon for cyber battles.",
                        "category": "Weapon",
                        "quantity": 3,
                        "price": 1200.0,
                        "creator_id": 1,
                        "owner_id": 42
                    }
                ]
            }
        }
