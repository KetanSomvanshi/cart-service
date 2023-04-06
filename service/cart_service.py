import http

from controller.context_manager import context_log_meta, context_actor_user_data
from data_adapter.cart import CustomerCart
from logger import logger
from models.base import GenericResponseModel
from models.cart import CartModel


class CartService:
    ERROR_NO_CART_FOR_CUSTOMER = "No cart found for customer"

    @staticmethod
    def get_cart_for_customer() -> GenericResponseModel:
        cart: CartModel = CustomerCart.get_by_customer_uuid(context_actor_user_data.get().uuid)
        if not cart:
            logger.error(extra=context_log_meta.get(), msg=f"No cart found for customer")
            return GenericResponseModel(status_code=http.HTTPStatus.NOT_FOUND,
                                        error=CartService.ERROR_NO_CART_FOR_CUSTOMER)
        return GenericResponseModel(status_code=http.HTTPStatus.OK, data=cart.build_response_model())
