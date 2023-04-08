from typing import List

from sqlalchemy import Column, String, Float, INTEGER
from sqlalchemy.orm import Session

from data_adapter.db import CartDBBase, DBBase
from models.inventory import ItemModel


class Item(DBBase, CartDBBase):
    __tablename__ = 'item'

    category = Column(String(255), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(String(5000), nullable=True)
    price = Column(Float, nullable=False)
    image = Column(String(1000), nullable=True)
    quantity = Column(INTEGER, nullable=False)

    def __to_model(self) -> ItemModel:
        """converts db orm object to pydantic model"""
        return ItemModel.from_orm(self)

    @classmethod
    def create_item(cls, item) -> ItemModel:
        from controller.context_manager import get_db_session
        db: Session = get_db_session()
        db.add(item)
        db.flush()
        return item.__to_model()

    @classmethod
    def get_by_id(cls, id) -> ItemModel:
        item = super().get_by_id(id)
        return item.__to_model() if item else None

    @classmethod
    def get_by_uuid(cls, uuid) -> ItemModel:
        item = super().get_by_uuid(uuid)
        return item.__to_model() if item else None

    @classmethod
    def get_all_items(cls) -> List[ItemModel]:
        from controller.context_manager import get_db_session
        db = get_db_session()
        items = db.query(cls).filter(cls.is_deleted.is_(False)).all()
        return [item.__to_model() for item in items]

    @classmethod
    def decrease_item_quantity(cls, item_uuid: str, quantity_to_reduce: int) -> int:
        from controller.context_manager import get_db_session
        db = get_db_session()
        updates = db.query(cls).filter(cls.uuid == item_uuid, cls.is_deleted.is_(False)).update(
            {cls.quantity: cls.quantity - quantity_to_reduce})
        db.flush()
        return updates

    @classmethod
    def increase_item_quantity(cls, item_uuid: str, quantity_to_increase: int) -> int:
        from controller.context_manager import get_db_session
        db = get_db_session()
        updates = db.query(cls).filter(cls.uuid == item_uuid, cls.is_deleted.is_(False)).update(
            {cls.quantity: cls.quantity + quantity_to_increase})
        db.flush()
        return updates

    @classmethod
    def get_by_name_and_category(cls, name: str, category: str) -> ItemModel:
        from controller.context_manager import get_db_session
        db = get_db_session()
        item = db.query(cls).filter(cls.name == name, cls.category == category, cls.is_deleted.is_(False)).first()
        return item.__to_model() if item else None
