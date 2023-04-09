import http

from fastapi import APIRouter, Depends

from controller.context_manager import build_request_context
from models.base import GenericResponseModel
from models.user import UserInsertModel, UserLoginModel
from service.user_service import UserService
from utils.helper import build_api_response

user_router = APIRouter(prefix="/v1/user", tags=["user"])


@user_router.post("/signup", status_code=http.HTTPStatus.CREATED, response_model=GenericResponseModel)
async def signup_user(user: UserInsertModel, _=Depends(build_request_context)):
    """
    Sign up user
    :param _: build_request_context dependency injection handles the request context
    :param user: user details to add
    :return:
    """
    response: GenericResponseModel = UserService.signup_user(user=user)
    return build_api_response(response)


@user_router.post("/login", status_code=http.HTTPStatus.OK, response_model=GenericResponseModel)
async def login_user(user_login_request: UserLoginModel, _=Depends(build_request_context)):
    """
    Login user
    :param _: build_request_context dependency injection handles the request context
    :param user_login_request: user login details
    :return: GenericResponseModel
    """
    response: GenericResponseModel = UserService.login_user(user_login_request=user_login_request)
    return build_api_response(response)
