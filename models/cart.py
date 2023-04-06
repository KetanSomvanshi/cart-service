from typing import List, Optional

from pydantic import BaseModel, validator

from models.base import DBBaseModel
from models.inventory import ItemModel, ItemCartResponseModel
from models.user import UserModel, UserResponseModel


class AddItemToCart(BaseModel):
    """Add item to cart model"""
    quantity: int = 0

    @validator('quantity')
    def quantity_must_be_positive(cls, v):
        if v < 0:
            raise ValueError('Quantity must be at least 0')
        return v


class CartResponseModel(BaseModel):
    """Cart response model"""
    cart_items: List[ItemCartResponseModel] = []
    customer: UserResponseModel
    total_price: float


class CartItemModel(DBBaseModel, BaseModel):
    """ Cart Item DB Model"""
    cart_id: int
    item_id: int
    quantity: int
    item: ItemModel

    class Config:
        orm_mode = True

    def build_item_cart_response_model(self) -> ItemCartResponseModel:
        return ItemCartResponseModel(**self.item.dict())


class CartModel(DBBaseModel, BaseModel):
    """Base DB model for cart"""
    cart_items: List[CartItemModel] = []
    total_price: float
    customer: UserModel
    customer_id: int

    class Config:
        orm_mode = True

    def build_response_model(self) -> CartResponseModel:
        return CartResponseModel(cart_items=[item.build_item_cart_response_model() for item in self.cart_items],
                                 customer=self.customer.build_response_model(), total_price=self.total_price)
