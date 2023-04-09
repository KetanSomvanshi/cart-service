from enum import Enum
from functools import wraps

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer

from controller.context_manager import context_actor_user_data
from models.user import UserRole
from utils.exceptions import AppException
from utils.jwt_token_handler import JWTHandler


class RBACResource(str, Enum):
    customer = "customer"
    inventory = "inventory"
    cart = "cart"


class RBACAccessType(str, Enum):
    read = "read"
    write = "write"
    delete = "delete"
    update = "update"


# resource to role mapping for RBAC
RBAC_MAPPER = {
    # admin can suspend customer
    RBACResource.customer: {RBACAccessType.delete: [UserRole.ADMIN]},
    # admin can add,update,read,delete items to inventory
    # customer can only read items from inventory
    RBACResource.inventory: {RBACAccessType.read: [UserRole.CUSTOMER, UserRole.ADMIN],
                             RBACAccessType.write: [UserRole.ADMIN],
                             RBACAccessType.update: [UserRole.ADMIN],
                             RBACAccessType.delete: [UserRole.ADMIN]},
    #  admin cannot do anything with customer cart , customer can do everything with cart
    RBACResource.cart: {RBACAccessType.read: [UserRole.CUSTOMER],
                        RBACAccessType.write: [UserRole.CUSTOMER],
                        RBACAccessType.update: [UserRole.CUSTOMER],
                        RBACAccessType.delete: [UserRole.CUSTOMER]}
}

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def rbac_access_checker(resource: RBACResource, rbac_access_type: RBACAccessType = RBACAccessType.read):
    """
    RBAC access checker decorator for endpoints to check if the user has access to the resource or not based on the role
    and acces_type provided
    :param rbac_access_type:  access type
    :param resource:  resource name
    :return:
    """

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Check if the user has access to the resource or not based on the role
            #  get user data from context
            if context_actor_user_data.get().role not in RBAC_MAPPER.get(resource).get(rbac_access_type, []):
                raise AppException(status_code=403, message=f"You are not allowed to access resource {resource}"
                                                            f" with operation {rbac_access_type}")
            return await func(*args, **kwargs)

        return wrapper

    return decorator


async def authenticate_token(token: str = Depends(oauth2_scheme)):
    # Decode the token and set the user data in context
    JWTHandler.decode_access_token(token=token)
