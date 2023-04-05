import http

from controller.context_manager import context_log_meta
from data_adapter.user import User
from logger import logger
from models.base import GenericResponseModel
from models.user import UserInsertModel
from utils.password_hasher import PasswordHasher


class UserService:
    USER_CREATED_SUCCESS = "User created successfully"

    @staticmethod
    def signup_user(user: UserInsertModel) -> GenericResponseModel:
        """
        Sign up user
        :param user: user details to add
        :return: GenericResponseModel
        """
        hashed_password = PasswordHasher.get_password_hash(user.password)
        user_to_create = user.create_db_entity(password_hash=hashed_password)
        User.create_user(user_to_create)
        logger.info(extra=context_log_meta.get(),
                    msg="User created successfully with uuid {}".format(user_to_create.uuid))
        return GenericResponseModel(status_code=http.HTTPStatus.CREATED, message=UserService.USER_CREATED_SUCCESS)
