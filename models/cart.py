from typing import List
from uuid import UUID

from pydantic import BaseModel, validator

from models.base import DBBaseModel
from models.inventory import ItemModel, ItemResponseModel
from models.user import UserModel, UserResponseModel


class CartItemQuantity(BaseModel):
    """Add item to cart model"""
    quantity: int = 1

    @validator('quantity')
    def quantity_must_be_positive(cls, v):
        if v < 1:
            raise ValueError('Quantity must be at least 1')
        return v


class CartItemResponseModel(BaseModel):
    """Cart item response model"""
    original_item: ItemResponseModel
    uuid: UUID
    quantity_in_cart: int


class CartResponseModel(BaseModel):
    """Cart response model"""
    cart_items: List[CartItemResponseModel] = []
    customer: UserResponseModel
    total_price: float


class CartItemModel(DBBaseModel, BaseModel):
    """ Cart Item DB Model"""
    cart_id: int
    item_id: int
    quantity_in_cart: int
    original_item: ItemModel

    class Config:
        orm_mode = True

    def build_response_model(self) -> CartItemResponseModel:
        return CartItemResponseModel(quantity_in_cart=self.quantity_in_cart, uuid=self.uuid,
                                     original_item=self.original_item.build_response_model())


class CartModel(DBBaseModel, BaseModel):
    """Base DB model for cart"""
    cart_items: List[CartItemModel] = []
    customer: UserModel
    customer_id: int

    @property
    def total_price(self) -> float:
        return sum([item.original_item.price*item.quantity_in_cart for item in self.cart_items])

    class Config:
        orm_mode = True

    def build_response_model(self) -> CartResponseModel:
        return CartResponseModel(cart_items=[cart_item.build_response_model() for cart_item in self.cart_items],
                                 customer=self.customer.build_response_model(), total_price=self.total_price)
