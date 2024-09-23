from typing import List
from pydantic import BaseModel, EmailStr

from inventory.schemas import ItemRead


class UserBase(BaseModel):
    username: str
    email: EmailStr


class UserCreate(UserBase):
    password: str


class UserRead(UserBase):
    id: int
    is_active: bool
    is_superuser: bool
    inventory: List[ItemRead]

    class Config:
        from_attributes = True

