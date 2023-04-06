from typing import List

from pydantic import BaseModel

from models.base import DBBaseModel
from models.inventory import ItemModel, ItemCartResponseModel
from models.user import UserModel, UserResponseModel


class CartResponseModel(BaseModel):
    """Cart response model"""
    cart_items: List[ItemCartResponseModel] = []
    customer: UserResponseModel
    total_price: float


class CartModel(DBBaseModel, BaseModel):
    """Base DB model for cart"""
    cart_items: List[ItemModel] = []
    total_price: float
    customer: UserModel
    customer_id: int

    class Config:
        orm_mode = True

    def build_response_model(self) -> CartResponseModel:
        return CartResponseModel(items=[item.build_item_cart_response_model() for item in self.cart_items],
                                 customer=self.customer.build_response_model(), total_price=self.total_price)
