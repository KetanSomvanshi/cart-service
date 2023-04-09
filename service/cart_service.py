import http
from uuid import UUID

from controller.context_manager import context_log_meta, context_actor_user_data
from data_adapter.cart import CustomerCart, CartItem
from data_adapter.inventory import Item
from data_adapter.user import User
from logger import logger
from models.base import GenericResponseModel
from models.cart import CartModel, CartItemQuantity, CartItemModel
from models.inventory import ItemModel
from models.user import UserModel


class CartService:
    ERROR_NO_CART_FOR_CUSTOMER = "No cart found for customer"
    ERROR_CUSTOMER_NOT_FOUND = "Customer not found"
    ERROR_ITEM_NOT_FOUND = "Item not found"
    ERROR_ITEM_QUANTITY_NOT_ENOUGH = "Item quantity not enough"
    ERROR_ITEM_OUT_OF_STOCK = "Item is out of stock"
    ERROR_ITEM_NOT_FOUND_IN_CART = "Item not found in cart"
    ERROR_CART_ITEM_NOT_FOUND = "Cart item not found"
    ERROR_CUSTOMER_CART_NOT_FOUND = "Customer cart not found"
    ERROR_CART_ITEM_QUANTITY_NOT_ENOUGH = "Cart item quantity not enough"

    @staticmethod
    def get_cart_for_customer() -> GenericResponseModel:
        cart: CartModel = CustomerCart.get_by_customer_uuid(context_actor_user_data.get().uuid)
        if not cart:
            logger.error(extra=context_log_meta.get(),
                         msg=f"No cart found for customer {context_actor_user_data.get().uuid}")
            return GenericResponseModel(status_code=http.HTTPStatus.NOT_FOUND,
                                        error=CartService.ERROR_NO_CART_FOR_CUSTOMER)
        return GenericResponseModel(status_code=http.HTTPStatus.OK, data=cart.build_response_model())

    @staticmethod
    def add_item_to_cart(item_uuid: UUID, add_item_request: CartItemQuantity) -> GenericResponseModel:
        """
        Add item to cart
        :param item_uuid:
        :param add_item_request:
        :return:

        logic for add cart item -
        1. validations like item exists , item quantity is enough , item is not out of stock
        2. reduce item quantity in inventory
        3. add item to cart , if cart not found for customer , create it
        4. if item already exists in cart , update quantity instead of adding same item to cart
        5. if item quantity is 0 , remove item from cart

        edge cases -
        1. if item is out of stock , then item should not be added to cart this is handled
        2. if 2 requests from different users are made to add same item to cart , and item quantity is not enough in
        that case one of the request would try to update item quantity as negative where database check would fail
        and only one of the request would be successful
        """
        item_to_add: ItemModel = Item.get_by_uuid(item_uuid)
        if not item_to_add:
            logger.error(extra=context_log_meta.get(), msg=f"Item not found {item_uuid}")
            return GenericResponseModel(status_code=http.HTTPStatus.NOT_FOUND, error=CartService.ERROR_ITEM_NOT_FOUND)
        if item_to_add.quantity <= 0:
            logger.error(extra=context_log_meta.get(), msg=f"Item is out of stock {item_uuid}")
            return GenericResponseModel(status_code=http.HTTPStatus.BAD_REQUEST,
                                        error=CartService.ERROR_ITEM_OUT_OF_STOCK)
        if item_to_add.quantity < add_item_request.quantity:
            logger.error(extra=context_log_meta.get(), msg=f"Item quantity not enough {item_uuid}")
            return GenericResponseModel(status_code=http.HTTPStatus.BAD_REQUEST,
                                        error=CartService.ERROR_ITEM_QUANTITY_NOT_ENOUGH)
        customer_cart: CartModel = CustomerCart.get_by_customer_uuid(context_actor_user_data.get().uuid)
        if not customer_cart:
            #  create cart if not yet created
            logger.info(extra=context_log_meta.get(),
                        msg=f"No cart found for customer {context_actor_user_data.get()} , so creating it")
            customer: UserModel = User.get_by_uuid(context_actor_user_data.get().uuid)
            if not customer:
                logger.error(extra=context_log_meta.get(),
                             msg=f"Customer not found , wrong uuid {context_actor_user_data.get().uuid}")
                return GenericResponseModel(status_code=http.HTTPStatus.NOT_FOUND,
                                            error=CartService.ERROR_CUSTOMER_NOT_FOUND)
            customer_cart = CustomerCart.create_cart_for_customer(customer.id)
        # reduce item quantity in inventory after validations
        Item.decrease_item_quantity(str(item_uuid), add_item_request.quantity)
        # update item quantity
        item_to_add.quantity -= add_item_request.quantity
        #  check if item is already in cart if exists , update quantity instead of adding same item to cart
        for cart_item in customer_cart.cart_items:
            if cart_item.item_id == item_to_add.id:
                # update quantity
                CartItem.update_item_quantity_in_cart(cart_item_id=cart_item.id,
                                                      quantity=cart_item.quantity_in_cart + add_item_request.quantity)
                # update response data
                cart_item.quantity_in_cart += add_item_request.quantity
                cart_item.original_item = item_to_add
                return GenericResponseModel(status_code=http.HTTPStatus.OK, data=customer_cart.build_response_model())
        # add item to cart if already not exists
        cart_item_added: CartItemModel = CartItem.add_item_to_cart(cart_id=customer_cart.id, item_id=item_to_add.id,
                                                                   quantity=add_item_request.quantity)
        #  update response data
        customer_cart.cart_items.append(cart_item_added)
        logger.info(extra=context_log_meta.get(), msg=f"Item added to cart {cart_item_added}")
        return GenericResponseModel(status_code=http.HTTPStatus.CREATED, data=customer_cart.build_response_model())

    @staticmethod
    def remove_item_from_cart(cart_item_uuid: UUID, remove_item_request: CartItemQuantity) -> GenericResponseModel:
        """
        Remove item from cart
        :param cart_item_uuid:
        :param remove_item_request:
        :return: GenericResponseModel

        logic for remove cart item -
        1. validations like if item exists in cart , if cart exists for customer
        2. if cart item quantity is 0 , remove item from cart
        3. if cart item quantity is not 0 , update item quantity in cart
        """
        cart_item_to_update: CartItemModel = CartItem.get_by_uuid(cart_item_uuid)
        if not cart_item_to_update:
            logger.error(extra=context_log_meta.get(), msg=f"Cart item to remove not found for uuid {cart_item_uuid}")
            return GenericResponseModel(status_code=http.HTTPStatus.NOT_FOUND,
                                        error=CartService.ERROR_CART_ITEM_NOT_FOUND)
        customer_cart: CartModel = CustomerCart.get_by_customer_uuid(context_actor_user_data.get().uuid)
        if not customer_cart or customer_cart.id != cart_item_to_update.cart_id:
            logger.error(extra=context_log_meta.get(),
                         msg=f"Customer cart not found for customer uuid {context_actor_user_data.get().uuid}")
            return GenericResponseModel(status_code=http.HTTPStatus.NOT_FOUND,
                                        error=CartService.ERROR_CUSTOMER_CART_NOT_FOUND)
        if cart_item_to_update.quantity_in_cart < remove_item_request.quantity:
            logger.error(extra=context_log_meta.get(), msg=f"Cart item quantity is less than requested quantity"
                                                           f" {cart_item_to_update.quantity_in_cart}")
            return GenericResponseModel(status_code=http.HTTPStatus.BAD_REQUEST,
                                        error=CartService.ERROR_CART_ITEM_QUANTITY_NOT_ENOUGH)
        #  update item quantity in inventory
        Item.increase_item_quantity(str(cart_item_to_update.original_item.uuid), remove_item_request.quantity)
        if cart_item_to_update.quantity_in_cart - remove_item_request.quantity == 0:
            # remove item from cart
            CartItem.delete_item_from_cart(cart_item_id=cart_item_to_update.id)
            # update response data
            customer_cart.cart_items = [cart_item for cart_item in customer_cart.cart_items if
                                        cart_item.id != cart_item_to_update.id]
            return GenericResponseModel(status_code=http.HTTPStatus.OK,
                                        data=customer_cart.build_response_model())
        # else update item quantity in cart
        CartItem.update_item_quantity_in_cart(
            cart_item_id=cart_item_to_update.id,
            quantity=cart_item_to_update.quantity_in_cart - remove_item_request.quantity)
        # update response data
        for cart_item in customer_cart.cart_items:
            if cart_item.id == cart_item_to_update.id:
                cart_item.quantity_in_cart -= remove_item_request.quantity
                cart_item.original_item.quantity += remove_item_request.quantity
                break
        return GenericResponseModel(status_code=http.HTTPStatus.OK, data=customer_cart.build_response_model())
