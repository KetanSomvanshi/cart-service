import http

from fastapi import APIRouter, Depends

from controller.context_manager import build_request_context
from models.base import GenericResponseModel
from server.auth import rbac_access_checker, RBACResource, RBACAccessType
from service.cart_service import CartService
from utils.helper import build_api_response

cart_router = APIRouter(prefix="/v1/cart", tags=["cart"])


@cart_router.get("", status_code=http.HTTPStatus.OK, response_model=GenericResponseModel)
@rbac_access_checker(resource=RBACResource.cart, rbac_access_type=RBACAccessType.read)
async def get_cart_items(_=Depends(build_request_context)):
    """
    Get all items from cart
    :param _: build_request_context dependency injection handles the request context
    :return: GenericResponseModel
    """
    response: GenericResponseModel = CartService.get_cart_for_customer()
    return build_api_response(response)
