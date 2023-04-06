import http
from uuid import UUID

from controller.context_manager import context_log_meta, context_actor_user_data
from data_adapter.cart import CustomerCart, CartItem
from data_adapter.inventory import Item
from data_adapter.user import User
from logger import logger
from models.base import GenericResponseModel
from models.cart import CartModel, CartItemQuantity
from models.inventory import ItemModel
from models.user import UserModel


class CartService:
    ERROR_NO_CART_FOR_CUSTOMER = "No cart found for customer"
    ERROR_CUSTOMER_NOT_FOUND = "Customer not found"
    ERROR_ITEM_NOT_FOUND = "Item not found"
    ERROR_ITEM_QUANTITY_NOT_ENOUGH = "Item quantity not enough"
    ERROR_ITEM_OUT_OF_STOCK = "Item is out of stock"

    @staticmethod
    def get_cart_for_customer() -> GenericResponseModel:
        cart: CartModel = CustomerCart.get_by_customer_uuid(context_actor_user_data.get().uuid)
        if not cart:
            logger.error(extra=context_log_meta.get(), msg=f"No cart found for customer")
            return GenericResponseModel(status_code=http.HTTPStatus.NOT_FOUND,
                                        error=CartService.ERROR_NO_CART_FOR_CUSTOMER)
        return GenericResponseModel(status_code=http.HTTPStatus.OK, data=cart.build_response_model())

    @staticmethod
    def add_item_to_cart(item_uuid: UUID, add_item_request: CartItemQuantity) -> GenericResponseModel:
        item_to_add: ItemModel = Item.get_by_uuid(item_uuid)
        if not item_to_add:
            logger.error(extra=context_log_meta.get(), msg=f"Item not found")
            return GenericResponseModel(status_code=http.HTTPStatus.NOT_FOUND, error=CartService.ERROR_ITEM_NOT_FOUND)
        if item_to_add.quantity == 0:
            logger.error(extra=context_log_meta.get(), msg=f"Item is out of stock")
            return GenericResponseModel(status_code=http.HTTPStatus.BAD_REQUEST,
                                        error=CartService.ERROR_ITEM_OUT_OF_STOCK)
        if item_to_add.quantity < add_item_request.quantity:
            logger.error(extra=context_log_meta.get(), msg=f"Item quantity not enough")
            return GenericResponseModel(status_code=http.HTTPStatus.BAD_REQUEST,
                                        error=CartService.ERROR_ITEM_QUANTITY_NOT_ENOUGH)
        customer_cart: CartModel = CustomerCart.get_by_customer_uuid(context_actor_user_data.get().uuid)
        if not customer_cart:
            #  create cart if not yet created
            logger.info(extra=context_log_meta.get(), msg=f"No cart found for customer , so creating it")
            customer: UserModel = User.get_by_uuid(context_actor_user_data.get().uuid)
            if not customer:
                logger.error(extra=context_log_meta.get(), msg=f"Customer not found , wrong uuid")
                return GenericResponseModel(status_code=http.HTTPStatus.NOT_FOUND,
                                            error=CartService.ERROR_CUSTOMER_NOT_FOUND)
            customer_cart = CustomerCart.create_cart_for_customer(customer.id)
        # reduce item quantity
        Item.update_item_by_uuid(str(item_uuid),
                                 update_dict={Item.quantity: item_to_add.quantity - add_item_request.quantity})
        # add item to cart
        CartItem.add_item_to_cart(cart_id=customer_cart.id, item_id=item_to_add.id,
                                  quantity=add_item_request.quantity)
        return GenericResponseModel(status_code=http.HTTPStatus.CREATED, data=customer_cart.build_response_model())

    @staticmethod
    def remove_item_from_cart(item_uuid: UUID, remove_item_request: CartItemQuantity) -> GenericResponseModel:
        item_to_remove: ItemModel = Item.get_by_uuid(item_uuid)
        if not item_to_remove:
            logger.error(extra=context_log_meta.get(), msg=f"Item not found")
            return GenericResponseModel(status_code=http.HTTPStatus.NOT_FOUND, error=CartService.ERROR_ITEM_NOT_FOUND)
        customer_cart: CartModel = CustomerCart.get_by_customer_uuid(context_actor_user_data.get().uuid)
        if not customer_cart:
            logger.error(extra=context_log_meta.get(), msg=f"No cart found for customer")
            return GenericResponseModel(status_code=http.HTTPStatus.NOT_FOUND,
                                        error=CartService.ERROR_NO_CART_FOR_CUSTOMER)
        # remove item from cart
        CartItem.remove_item_from_cart(cart_id=customer_cart.id, item_id=item_to_remove.id,
                                       quantity=remove_item_request.quantity)
        # increase item quantity
        Item.update_item_by_uuid(str(item_uuid),
                                 update_dict={Item.quantity: item_to_remove.quantity + remove_item_request.quantity})
        return GenericResponseModel(status_code=http.HTTPStatus.OK, data=customer_cart.build_response_model())

