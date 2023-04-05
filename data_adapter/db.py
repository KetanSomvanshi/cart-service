from datetime import datetime
from urllib.parse import quote_plus

from pytz import timezone
from sqlalchemy import Column, TIMESTAMP, Boolean, Integer, create_engine, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, scoped_session
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
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        # to be executed when request closes
        db.commit()
        db.close()


class DBBase:
    """Base class for all db orm models"""
    id = Column(Integer, primary_key=True, unique=True, autoincrement=True)
    external_id = Column(String(255), unique=True)
    created_at = Column(TIMESTAMP(timezone=True), default=time_now, nullable=False)
    updated_at = Column(TIMESTAMP(timezone=True), default=time_now, onupdate=time_now, nullable=False)
    is_deleted = Column(Boolean, default=False)
