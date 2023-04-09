from sqlalchemy import Column, INTEGER, ForeignKey
from sqlalchemy.orm import relationship, contains_eager

from data_adapter.db import CartDBBase, DBBase
from data_adapter.inventory import Item
from data_adapter.user import User
from models.cart import CartModel, CartItemModel


class CustomerCart(DBBase, CartDBBase):
    __tablename__ = 'customer_cart'

    # foreign key form user table
    customer_id = Column(INTEGER, ForeignKey(User.id), nullable=False)

    #  relationship one to many with cart item
    cart_items = relationship('CartItem', back_populates='cart')
    #  relationship one to one with user
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
        #  using eager loading to avoid CartItem filter not getting applied
        user_cart = db.query(cls).join(cls.customer).join(CartItem). \
            filter(User.uuid == customer_uuid, cls.is_deleted.is_(False), CartItem.is_deleted.is_(False)).options(
            contains_eager(cls.cart_items)).first()
        return user_cart.__to_model() if user_cart else None

    @classmethod
    def create_cart_for_customer(cls, customer_id: int) -> CartModel:
        from controller.context_manager import get_db_session
        db = get_db_session()
        user_cart = cls(customer_id=customer_id)
        db.add(user_cart)
        db.flush()
        return user_cart.__to_model()


class CartItem(DBBase, CartDBBase):
    __tablename__ = 'cart_item'

    item_id = Column(INTEGER, ForeignKey(Item.id), nullable=False)
    cart_id = Column(INTEGER, ForeignKey(CustomerCart.id), nullable=False)
    quantity_in_cart = Column(INTEGER, nullable=False)

    # relationship many to one with cart
    cart = relationship(CustomerCart, back_populates='cart_items')
    # relationship many to one with item
    original_item = relationship('Item')

    def __to_model(self) -> CartItemModel:
        """converts db orm object to pydantic model"""
        return CartItemModel.from_orm(self)

    def get_model(self) -> CartItemModel:
        return self.__to_model()

    @classmethod
    def add_item_to_cart(cls, cart_id: int, item_id: int, quantity: int) -> CartItemModel:
        from controller.context_manager import get_db_session
        db = get_db_session()
        cart_item = cls(cart_id=cart_id, item_id=item_id, quantity_in_cart=quantity)
        db.add(cart_item)
        db.flush()
        return cart_item.__to_model()

    @classmethod
    def delete_item_from_cart(cls, cart_item_id: int):
        from controller.context_manager import get_db_session
        db = get_db_session()
        db.query(cls).filter(cls.id == cart_item_id).update({cls.is_deleted: True, cls.quantity_in_cart: 0})
        db.flush()

    @classmethod
    def update_item_quantity_in_cart(cls, cart_item_id: int, quantity: int):
        from controller.context_manager import get_db_session
        db = get_db_session()
        db.query(cls).filter(cls.id == cart_item_id).update({cls.quantity_in_cart: quantity})
        db.flush()
