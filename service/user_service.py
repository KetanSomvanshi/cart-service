import http

from controller.context_manager import context_log_meta
from data_adapter.user import User
from logger import logger
from models.base import GenericResponseModel
from models.user import UserInsertModel, UserLoginModel, UserModel, UserTokenResponseModel
from utils.jwt_token_handler import JWTHandler
from utils.password_hasher import PasswordHasher


class UserService:
    MSG_USER_CREATED_SUCCESS = "User created successfully"
    MSG_USER_LOGIN_SUCCESS = "Login successful"
    MSG_USER_SUSPENDED = "User is suspended successfully"

    ERROR_INVALID_CREDENTIALS = "Invalid credentials"
    ERROR_USER_NOT_FOUND = "User not found"

    @staticmethod
    def signup_user(user: UserInsertModel) -> GenericResponseModel:
        """
        Sign up user
        :param user: user details to add
        :return: GenericResponseModel
        """
        hashed_password = PasswordHasher.get_password_hash(user.password)
        user_to_create = user.create_db_entity(password_hash=hashed_password)
        user_data = User.create_user(user_to_create)
        logger.info(extra=context_log_meta.get(),
                    msg="User created successfully with uuid {}".format(user_to_create.uuid))
        return GenericResponseModel(status_code=http.HTTPStatus.CREATED, message=UserService.MSG_USER_CREATED_SUCCESS,
                                    data=user_data.build_response_model())

    @staticmethod
    def login_user(user_login_request: UserLoginModel) -> GenericResponseModel:
        """
        Login user
        :param user_login_request: user login details
        :return: GenericResponseModel
        """
        user: UserModel = User.get_active_user_by_email(user_login_request.email)
        if not user:
            logger.error(extra=context_log_meta.get(), msg=f"user not found for email {user_login_request.email}")
            return GenericResponseModel(status_code=http.HTTPStatus.UNAUTHORIZED,
                                        error=UserService.ERROR_USER_NOT_FOUND)
        if PasswordHasher.verify_password(user_login_request.password, user.password_hash):
            token = JWTHandler.create_access_token(user.build_user_token_data())
            logger.info(extra=context_log_meta.get(), msg=f"Login successful for user {user.email}"
                                                          f" with token {token}")
            #  return token to client for further use
            return GenericResponseModel(status_code=http.HTTPStatus.OK, data=UserTokenResponseModel(
                access_token=token, user_uuid=user.uuid, user_role=user.role, user_status=user.status),
                                        message=UserService.MSG_USER_LOGIN_SUCCESS)
        logger.error(extra=context_log_meta.get(), msg=f"Invalid credentials for user {user.email}")
        return GenericResponseModel(status_code=http.HTTPStatus.UNAUTHORIZED,
                                    error=UserService.ERROR_INVALID_CREDENTIALS)
