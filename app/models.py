from sqlalchemy import Column, Integer, String, Text, Float

from app.database import Base


class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, nullable=False)


class Item(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, nullable=False)
    description = Column(Text)
    category = Column(String(255), nullable=False)
    quantity = Column(Integer)
    price = Column(Float)
