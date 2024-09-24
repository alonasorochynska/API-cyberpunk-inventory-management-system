from sqlalchemy import Column, Integer, String, Text, Float, ForeignKey
from sqlalchemy.orm import relationship

from database import Base


class Category(Base):
    """
    Represents a category in the system.
    """
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, nullable=False)


class Item(Base):
    """
    Represents an item in the system, including relationships
    to the user who created it and its owner.
    """

    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, nullable=False)
    description = Column(Text)
    category = Column(String(255), nullable=False)
    quantity = Column(Integer)
    price = Column(Float)

    creator_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    creator = relationship(
        "User", back_populates="created_items", foreign_keys=[creator_id]
    )

    owner_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    owner = relationship(
        "User", back_populates="inventory", foreign_keys=[owner_id]
    )
