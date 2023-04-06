from sqlalchemy import Column, String

from sqlalchemy.orm import Session
from data_adapter.db import CartDBBase, DBBase
from models.user import UserModel, UserStatus, UserRole


class User(DBBase, CartDBBase):
    __tablename__ = 'user'

    first_name = Column(String(255), nullable=False)
    last_name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False)
    role = Column(String(20), nullable=False)
    password_hash = Column(String(255), nullable=False)
    status = Column(String(20), nullable=False)

    def __to_model(self) -> UserModel:
        """converts db orm object to pydantic model"""
        return UserModel.from_orm(self)

    @classmethod
    def create_user(cls, user) -> UserModel:
        from controller.context_manager import get_db_session
        db: Session = get_db_session()
        db.add(user)
        db.flush()
        return user.__to_model()

    @classmethod
    def get_by_id(cls, id) -> UserModel:
        user = super().get_by_id(id)
        return user.__to_model() if user else None

    @classmethod
    def get_by_uuid(cls, uuid) -> UserModel:
        user = super().get_by_uuid(uuid)
        return user.__to_model() if user else None

    @classmethod
    def get_active_user_by_email(cls, email) -> UserModel:
        from controller.context_manager import get_db_session
        db = get_db_session()
        user = db.query(cls).filter(cls.email == email, cls.status == UserStatus.ACTIVE,
                                    cls.is_deleted.is_(False)).first()
        return user.__to_model() if user else None

    @classmethod
    def update_user_by_uuid(cls, user_uuid: str, update_dict: dict, user_role: UserRole = None) -> int:
        from controller.context_manager import get_db_session
        db = get_db_session()
        update_query = db.query(cls).filter(cls.uuid == user_uuid, cls.is_deleted.is_(False))
        if user_role:
            update_query = update_query.filter(cls.role == user_role)
        updates = update_query.update(update_dict)
        db.flush()
        return updates
