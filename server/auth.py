from enum import Enum
from functools import wraps
from typing import List

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer

from controller.context_manager import context_actor_user_data
from models.user import UserRole
from utils.exceptions import AppException
from utils.jwt_token_handler import JWTHandler


class RBACResource(str, Enum):
    customer = "customer"


# resource to role mapping for RBAC
RBAC_MAPPER = {
    RBACResource.customer: [UserRole.ADMIN]}

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def rbac_access_checker(resource: RBACResource):
    """
    RBAC access checker decorator for endpoints to check if the user has access to the resource or not based on the role
    :param resource:  resource name
    :return:
    """

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Check if the user has access to the resource or not based on the role
            #  get user data from context
            if context_actor_user_data.get().role not in RBAC_MAPPER.get(resource):
                raise AppException(status_code=403, message=f"You are not allowed to access resource {resource}")
            return await func(*args, **kwargs)

        return wrapper

    return decorator


async def authenticate_token(token: str = Depends(oauth2_scheme)):
    # Decode the token and set the user data in context
    JWTHandler.decode_access_token(token=token)
