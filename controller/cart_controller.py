import http
from uuid import UUID

from fastapi import APIRouter, Depends
from fastapi.params import Path

from controller.context_manager import build_request_context
from models.base import GenericResponseModel
from models.cart import CartItemQuantity
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


@cart_router.post("/item/{item_uuid}", status_code=http.HTTPStatus.CREATED, response_model=GenericResponseModel)
@rbac_access_checker(resource=RBACResource.cart, rbac_access_type=RBACAccessType.write)
async def add_item_to_cart(add_item_request: CartItemQuantity,
                           item_uuid: UUID = Path(..., description="Item uuid to add to cart"),
                           _=Depends(build_request_context)):
    """
    Add item to cart
    :param add_item_request:  CartItemQuantity
    :param item_uuid:  item uuid of item to add to cart
    :param _: build_request_context dependency injection handles the request context
    :return: GenericResponseModel
    """
    response: GenericResponseModel = CartService.add_item_to_cart(item_uuid=item_uuid,
                                                                  add_item_request=add_item_request)
    return build_api_response(response)


@cart_router.delete("/item/{cart_item_uuid}", status_code=http.HTTPStatus.OK, response_model=GenericResponseModel)
@rbac_access_checker(resource=RBACResource.cart, rbac_access_type=RBACAccessType.delete)
async def remove_item_from_cart(remove_item_request: CartItemQuantity,
                                cart_item_uuid: UUID = Path(..., description="Item uuid to remove from cart"),
                                _=Depends(build_request_context)):
    """
    Remove item from cart
    :param remove_item_request:    CartItemQuantity object
    :param _: build_request_context dependency injection handles the request context
    :param cart_item_uuid: item uuid to remove from cart
    :return: GenericResponseModel
    """
    response: GenericResponseModel = CartService.remove_item_from_cart(cart_item_uuid=cart_item_uuid,
                                                                       remove_item_request=remove_item_request)
    return build_api_response(response)
