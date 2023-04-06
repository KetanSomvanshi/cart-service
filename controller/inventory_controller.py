import http

from fastapi import APIRouter, Depends

from controller.context_manager import build_request_context
from models.base import GenericResponseModel
from models.inventory import ItemInsertModel
from server.auth import rbac_access_checker, RBACResource, RBACAccessType
from service.inventory_service import InventoryService
from utils.helper import build_api_response

inventory_router = APIRouter(prefix="/v1/inventory/items", tags=["inventory", "items"])


@inventory_router.get("", status_code=http.HTTPStatus.OK, response_model=GenericResponseModel)
@rbac_access_checker(resource=RBACResource.inventory, rbac_access_type=RBACAccessType.read)
async def get_items_from_inventory(_=Depends(build_request_context)):
    """
    Get all items from inventory
    :param _: build_request_context dependency injection handles the request context
    :return: GenericResponseModel
    """
    response = InventoryService.get_all_items_in_inventory()
    return build_api_response(response)


@inventory_router.post("", status_code=http.HTTPStatus.CREATED, response_model=GenericResponseModel)
@rbac_access_checker(resource=RBACResource.inventory, rbac_access_type=RBACAccessType.write)
async def add_item_to_inventory(item: ItemInsertModel, _=Depends(build_request_context)):
    """
    Add item to inventory
    :param _: build_request_context dependency injection handles the request context
    :param item: item details to add
    :return:
    """
    response = InventoryService.add_item_to_inventory(item=item)
    return build_api_response(response)
