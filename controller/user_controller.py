import http

from fastapi import APIRouter, Depends, Query

from controller.context_manager import build_request_context
from models.base import GenericResponseModel
from models.user import UserInsertModel
from utils.helper import build_api_response

user_router = APIRouter(prefix="/v1/user/", tags=["user"])


@user_router.post("signup", status_code=http.HTTPStatus.OK)
async def signup_user(_=Depends(build_request_context), user: UserInsertModel = Depends()):
    """
    Sign up user
    :param _: build_request_context dependency injection handles the request context
    :param user: user details to add
    :return:
    """
    pass
