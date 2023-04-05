import http

from controller.context_manager import context_log_meta
from data_adapter.user import User
from logger import logger
from models.base import GenericResponseModel
from models.user import UserStatus, UserRole


class CustomerService:
    ERROR_CUSTOMER_NOT_FOUND = "Customer not found"

    MSG_CUSTOMER_SUSPENDED = "Customer is suspended successfully"

    @staticmethod
    def suspend_customer(customer_uuid: str) -> GenericResponseModel:
        """
        Suspend customer
        :param customer_uuid: customer uuid to suspend
        :return: GenericResponseModel
        """
        # only customer role user can be suspended
        updates = User.update_user_by_uuid(user_uuid=customer_uuid, user_role=UserRole.CUSTOMER,
                                           update_dict={User.status: UserStatus.SUSPENDED})
        if not updates:
            logger.error(extra=context_log_meta.get(), msg=f"User with uuid {customer_uuid} not found")
            return GenericResponseModel(status_code=http.HTTPStatus.NOT_FOUND,
                                        error=CustomerService.ERROR_CUSTOMER_NOT_FOUND)
        return GenericResponseModel(status_code=http.HTTPStatus.OK, message=CustomerService.MSG_CUSTOMER_SUSPENDED)
