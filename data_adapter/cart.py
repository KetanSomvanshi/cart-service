from sqlalchemy import Column, INTEGER, ForeignKey
from sqlalchemy.orm import relationship

from data_adapter.db import CartDBBase, DBBase
from data_adapter.inventory import Item
from data_adapter.user import User
from models.cart import CartModel


class CustomerCart(DBBase, CartDBBase):
    __tablename__ = 'customer_cart'

    customer_id = Column(INTEGER, ForeignKey(User.id), nullable=False)
    total_price = Column(INTEGER, nullable=False)

    cart_items = relationship('CartItem', back_populates='cart')
    customer = relationship(User)

    def __to_model(self) -> CartModel:
        """converts db orm object to pydantic model"""
        return CartModel.from_orm(self)

    @classmethod
    def get_by_id(cls, id) -> CartModel:
        user_cart = super().get_by_id(id)
        return user_cart.__to_model() if user_cart else None

    @classmethod
    def get_by_uuid(cls, uuid) -> CartModel:
        user_cart = super().get_by_uuid(uuid)
        return user_cart.__to_model() if user_cart else None

    @classmethod
    def get_by_customer_uuid(cls, customer_uuid: str) -> CartModel:
        from controller.context_manager import get_db_session
        db = get_db_session()
        user_cart = db.query(cls).join(cls.customer).filter(User.uuid == customer_uuid,
                                                            cls.is_deleted.is_(False)).first()
        return user_cart.__to_model() if user_cart else None


class CartItem(DBBase, CartDBBase):
    __tablename__ = 'cart_item'

    item_id = Column(INTEGER, ForeignKey(Item.id), nullable=False)
    cart_id = Column(INTEGER, ForeignKey(CustomerCart.id), nullable=False)
    quantity = Column(INTEGER, nullable=False)

    cart = relationship(CustomerCart, back_populates='cart_items')
    item = relationship('Item')
