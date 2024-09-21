from typing import Optional

from pydantic import BaseModel


class CategoryBase(BaseModel):
    name: str


class CategoryCreate(CategoryBase):
    pass


class Category(CategoryBase):
    id: int

    class Config:
        from_attributes = True


class ItemBase(BaseModel):
    name: str
    description: Optional[str] = None
    category: str
    quantity: int
    price: Optional[float] = 0


class ItemCreate(ItemBase):
    pass


class ItemRead(ItemBase):
    id: int
    owner_id: Optional[int] = None

    class Config:
        from_attributes = True
