from sqlalchemy import Column, Integer, String, Boolean
from fastapi_users_db_sqlalchemy import SQLAlchemyBaseUserTable
from sqlalchemy.orm import relationship

from app.database import Base


class User(Base, SQLAlchemyBaseUserTable):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)

    created_items = relationship("Item", back_populates="creator", foreign_keys="Item.creator_id")

    inventory = relationship("Item", back_populates="owner", foreign_keys="Item.owner_id")
