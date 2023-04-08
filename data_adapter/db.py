from datetime import datetime
from urllib.parse import quote_plus

import uuid as uuid
from pytz import timezone
from sqlalchemy import Column, TIMESTAMP, Boolean, Integer, create_engine
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session
from sqlalchemy.orm import sessionmaker

from config.settings import DB
from logger import logging

DBTYPE_POSTGRES = 'postgresql'
CORE_SQLALCHEMY_DATABASE_URI = '%s://%s:%s@%s:%s/%s' % (
    DBTYPE_POSTGRES, DB.user, quote_plus(DB.pass_), DB.host, DB.port, DB.name)

db_engine = create_engine(CORE_SQLALCHEMY_DATABASE_URI)

logging.getLogger('sqlalchemy.engine').setLevel(logging.DEBUG)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=db_engine)

UTC = timezone('UTC')


def time_now():
    return datetime.now(UTC)


DBBase = declarative_base()


def get_db():
    """this function is used to inject db_session dependency in every rest api requests"""
    from controller.context_manager import context_set_db_session_rollback
    db: Session = SessionLocal()
    try:
        yield db
        #  commit the db session if no exception occurs
        #  if context_set_db_session_rollback is set to True then rollback the db session
        if context_set_db_session_rollback.get():
            logging.info('rollback db session')
            db.rollback()
        else:
            db.commit()
    except Exception as e:
        #  rollback the db session if any exception occurs
        logging.error(e)
        db.rollback()
    finally:
        #  close the db session
        db.close()


class CartDBBase:
    """Base class for all db orm models"""
    id = Column(Integer, primary_key=True, unique=True, autoincrement=True)
    uuid = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True)
    created_at = Column(TIMESTAMP(timezone=True), default=time_now, nullable=False)
    updated_at = Column(TIMESTAMP(timezone=True), default=time_now, onupdate=time_now, nullable=False)
    is_deleted = Column(Boolean, default=False)

    @classmethod
    def get_by_uuid(cls, uuid):
        from controller.context_manager import get_db_session
        db: Session = get_db_session()
        return db.query(cls).filter(cls.uuid == uuid, cls.is_deleted.is_(False)).first()

    @classmethod
    def get_by_id(cls, id):
        from controller.context_manager import get_db_session
        db: Session = get_db_session()
        return db.query(cls).filter(cls.id == id, cls.is_deleted.is_(False)).first()
