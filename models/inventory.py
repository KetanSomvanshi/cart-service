from enum import Enum
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, validator, HttpUrl

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
    image: Optional[HttpUrl] = None

    @validator('price')
    def price_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError('Price must be positive')
        return v

    @validator('quantity')
    def quantity_must_be_positive(cls, v):
        if v < 1:
            raise ValueError('Quantity must be at least 1')
        return v


class ItemResponseModel(ItemInsertModel):
    uuid: UUID


class ItemModel(ItemInsertModel, DBBaseModel):
    pass

    class Config:
        orm_mode = True

    def build_response_model(self) -> ItemResponseModel:
        return ItemResponseModel(**self.dict())
