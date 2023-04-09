from datetime import datetime
from typing import Optional, Any
from uuid import UUID

from pydantic.main import BaseModel


class GenericResponseModel(BaseModel):
    """Generic response model for all responses"""
    api_id: Optional[str] = None
    error: Optional[str]
    message: Optional[str]
    data: Any
    status_code: Optional[int] = None


class DBBaseModel(BaseModel):
    """Base model for all models that will be stored in the database"""
    id: int
    uuid: UUID
    created_at: datetime
    updated_at: Optional[datetime]
    is_deleted: bool

    class Config:
        orm_mode = True
