from enum import Enum
from typing import Optional

from pydantic import BaseModel

from models.base import DBBaseModel


class ItemCategory(str, Enum):
    """Item category"""
    ELECTRONICS = 'electronics'
    CLOTHING = 'clothing'
    BOOKS = 'books'
    TOYS = 'toys'
    GROCERIES = 'groceries'


class ItemInsertModel(BaseModel):
    category = ItemCategory
    name: str
    price: float
    description: Optional[str] = None
    quantity: int = 1


class ItemModel(ItemInsertModel, DBBaseModel):
    pass
