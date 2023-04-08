import http

from fastapi import APIRouter, Depends, Path

from controller.context_manager import build_request_context
from models.base import GenericResponseModel
from server.auth import rbac_access_checker, RBACResource, RBACAccessType
from service.customer_service import CustomerService
from utils.helper import build_api_response

customer_router = APIRouter(prefix="/v1/customer", tags=["customer"])


@customer_router.delete("/{customer_uuid}/suspend", status_code=http.HTTPStatus.OK, response_model=GenericResponseModel)
@rbac_access_checker(resource=RBACResource.customer, rbac_access_type=RBACAccessType.delete)
async def suspend_user(customer_uuid: str = Path(..., description="Customer uuid to suspend"),
                       _=Depends(build_request_context)):
    """
    Suspend customer
    :param _: build_request_context dependency injection handles the request context
    :param customer_uuid: user uuid to suspend
    :return: GenericResponseModel
    """
    response: GenericResponseModel = CustomerService.suspend_customer(customer_uuid=customer_uuid)
    return build_api_response(response)
