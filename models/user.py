from enum import Enum
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, validator, EmailStr

from models.base import DBBaseModel


class UserRole(str, Enum):
    """Enum for user roles"""
    ADMIN = "admin"
    CUSTOMER = "customer"


class UserStatus(str, Enum):
    """Enum for user status"""
    ACTIVE = "active"
    SUSPENDED = "suspended"


class UserTokenData(BaseModel):
    """User token data"""
    uuid: str
    role: UserRole
    email: EmailStr


class UserBaseModel(BaseModel):
    """User model for insert"""
    first_name: str
    last_name: str
    email: EmailStr
    role: UserRole = UserRole.CUSTOMER
    status: UserStatus = UserStatus.ACTIVE


class UserInsertModel(UserBaseModel):
    """User model for insert"""
    password: str

    @validator('password')
    def password_validator(cls, password):
        """
        Validates that the password is at least 8 characters long,
        contains at least one uppercase letter, one lowercase letter,
        one number, and one special character.
        """
        special_chars = {'!', '@', '#', '$', '%', '^', '&', '*', '(', ')', '-', '+', '='}
        if len(password) < 8:
            raise ValueError('password must be at least 8 characters long')
        if not any(char.isupper() for char in password):
            raise ValueError('password must contain at least one uppercase letter')
        if not any(char.islower() for char in password):
            raise ValueError('password must contain at least one lowercase letter')
        if not any(char.isdigit() for char in password):
            raise ValueError('password must contain at least one number')
        if not any(char in special_chars for char in password):
            raise ValueError('password must contain at least one special character')
        return password

    def create_db_entity(self, password_hash: str):
        """
        Creates a db entity from the insert model
        """
        from data_adapter.user import User
        dict_to_build_db_entity = self.dict()
        dict_to_build_db_entity['password_hash'] = password_hash
        dict_to_build_db_entity.pop('password')
        return User(**dict_to_build_db_entity)


class UserModel(UserBaseModel, DBBaseModel):
    """User model"""
    password_hash: str

    class Config:
        orm_mode = True

    def build_user_token_data(self) -> dict:
        """
        Builds the user token data
        :return: dict
        """
        res_dict = self.dict()
        res_dict['uuid'] = str(self.uuid)
        return UserTokenData.parse_obj(res_dict).dict()


class UserLoginModel(BaseModel):
    """User logincart model"""
    email: EmailStr
    password: str


class TokenType(str, Enum):
    bearer = "bearer"


class UserTokenResponseModel(BaseModel):
    """User token model"""
    access_token: str
    token_type: TokenType = TokenType.bearer
