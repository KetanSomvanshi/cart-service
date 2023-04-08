from enum import Enum
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, validator, HttpUrl, constr

from models.base import DBBaseModel


class ItemCategory(str, Enum):
    """Item category"""
    ELECTRONICS = 'electronics'
    CLOTHING = 'clothing'
    BOOKS = 'books'
    TOYS = 'toys'
    GROCERIES = 'groceries'


class ItemBaseModel(BaseModel):
    category: ItemCategory
    name: constr(min_length=1, max_length=255, strip_whitespace=True)
    price: float
    description: Optional[constr(min_length=1, max_length=5000, strip_whitespace=True)] = None
    image: Optional[HttpUrl] = None

    @validator('price')
    def price_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError('Price must be positive')
        return v


class ItemInsertModel(ItemBaseModel):
    """Item model for insert"""
    quantity: int = 0

    @validator('quantity')
    def quantity_must_be_positive(cls, v):
        if v < 0:
            raise ValueError('Quantity must be at least 0')
        return v

    def build_db_model(self):
        from data_adapter.inventory import Item
        return Item(**self.dict())


class ItemResponseModel(ItemInsertModel):
    """Item response model"""
    uuid: UUID


class ItemModel(ItemInsertModel, DBBaseModel):
    """Base DB model for item"""
    pass

    class Config:
        orm_mode = True

    def build_response_model(self) -> ItemResponseModel:
        return ItemResponseModel(**self.dict())
